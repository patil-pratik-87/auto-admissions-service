"""Production composition root for the local admissions screening runtime."""

import os
from pathlib import Path

from langsmith.wrappers import wrap_openai
from openai import OpenAI
from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.adapters.openai_model import OpenAIAdmissionsModelAdapter
from app.adapters.run_ids import UuidRunIds
from app.facts import FactsExtractor
from app.io.catalog import CatalogError, load_program_catalog
from app.rules_engine import PolicyActivationError, RulesEngine
from app.services.ports import AdmissionsModelPort
from app.services.screening import ScreeningConfig, ScreeningWorkflow

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class BootstrapError(Exception):
    """Safe configuration or activation error raised before an operation starts."""

    def __init__(self, code: str, safe_message: str, *, exit_code: int = 2) -> None:
        """Initialize one stable bootstrap failure."""
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.exit_code = exit_code


class AdmissionsSettings(BaseSettings):
    """Environment-backed configuration for the local composition root."""

    model_config = SettingsConfigDict(
        extra="ignore",
        frozen=True,
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
    )

    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "ADMISSIONS_OPENAI_API_KEY"),
    )
    openai_model: str = Field(
        default="gpt-5.4-mini",
        validation_alias="ADMISSIONS_OPENAI_MODEL",
    )
    catalog_path: Path = PROJECT_ROOT / "config" / "programs.yaml"
    rules_root: Path = PROJECT_ROOT / "rules"
    trace_enabled: bool = False
    langsmith_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="LANGSMITH_API_KEY",
    )
    langsmith_endpoint: str | None = Field(
        default=None,
        validation_alias="LANGSMITH_ENDPOINT",
    )
    langsmith_project: str = Field(
        default="auto-admissions",
        validation_alias="LANGSMITH_PROJECT",
    )

    @property
    def openai_key_value(self) -> str | None:
        """Return a non-empty provider credential when configured."""
        if self.openai_api_key is None:
            return None
        value = self.openai_api_key.get_secret_value().strip()
        return value or None

    @property
    def langsmith_key_value(self) -> str | None:
        """Return a non-empty tracing credential when configured."""
        if self.langsmith_api_key is None:
            return None
        value = self.langsmith_api_key.get_secret_value().strip()
        return value or None


def build_screening(settings: AdmissionsSettings) -> ScreeningWorkflow:
    """Compose all production adapters behind the synchronous public facade."""
    try:
        catalog = load_program_catalog(settings.catalog_path)
    except CatalogError as error:
        raise BootstrapError(error.code, error.safe_message) from error

    try:
        rules_engine = RulesEngine.activate(settings.rules_root)
    except PolicyActivationError as error:
        raise BootstrapError(error.code, error.safe_message, exit_code=6) from error

    for program in catalog.programs:
        if not rules_engine.has_policy(program.policy.id, program.policy.version):
            raise BootstrapError(
                "POLICY_NOT_ACTIVATED",
                "A configured program references a policy the rules package does not activate.",
                exit_code=6,
            )

    if settings.trace_enabled:
        langsmith_key = settings.langsmith_key_value
        if langsmith_key is None:
            raise BootstrapError(
                "LANGSMITH_API_KEY_MISSING",
                "LANGSMITH_API_KEY is required when tracing is enabled.",
            )
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = langsmith_key
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
        if settings.langsmith_endpoint is not None:
            os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint

    openai_key = settings.openai_key_value
    model_port: AdmissionsModelPort | None = None
    if openai_key is not None:
        openai_client = OpenAI(api_key=openai_key, max_retries=0)
        if settings.trace_enabled:
            openai_client = wrap_openai(openai_client)
        model_port = OpenAIAdmissionsModelAdapter(openai_client)

    return ScreeningWorkflow(
        catalog=catalog,
        facts_extractor=FactsExtractor(model=model_port),
        rules_engine=rules_engine,
        model_port=model_port,
        run_id_factory=UuidRunIds(),
        config=ScreeningConfig(default_model=settings.openai_model),
    )
