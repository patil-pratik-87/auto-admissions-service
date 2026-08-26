"""Stable private ports for model and redacted tracing boundaries."""

from enum import StrEnum
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.models.facts import ApplicationFacts
from app.models.programs import ProgramContext
from app.models.results import ApplicationResult, CanonicalSummary


class PortModel(BaseModel):
    """Base configuration for immutable, strict port payloads."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class PdfModelInput(PortModel):
    """Transient exact PDF bytes supplied to one extraction attempt."""

    document_id: str
    filename: str
    content: bytes


class ExtractApplicationFactsRequest(PortModel):
    """One provider attempt to extract final facts from a complete PDF bundle."""

    documents: tuple[PdfModelInput, ...] = Field(min_length=1)
    program: ProgramContext
    model: str
    prompt_version: str
    max_output_tokens: int = Field(gt=0)


class ParaphraseRequest(PortModel):
    """Completed deterministic result supplied to optional presentation only."""

    result: ApplicationResult
    canonical_summary: CanonicalSummary
    model: str
    prompt_version: str
    max_output_tokens: int = Field(gt=0)


class ParaphraseDraft(PortModel):
    """Optional plain-language restatement of a deterministic result."""

    text: str


class ProviderUsage(PortModel):
    """Token accounting returned by one provider attempt."""

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class ProviderSucceeded[U](PortModel):
    """Completed and parsed provider result for one attempt."""

    kind: Literal["SUCCEEDED"]
    output: U
    model_returned: str
    request_id: str | None = None
    usage: ProviderUsage
    duration_ms: int = Field(ge=0)


class ProviderRefused(PortModel):
    """Non-retryable provider refusal without dynamic applicant content."""

    kind: Literal["REFUSED"]
    code: Literal["PROVIDER_REFUSED"] = "PROVIDER_REFUSED"
    duration_ms: int = Field(ge=0)
    request_id: str | None = None


class IncompleteReason(StrEnum):
    """Safe provider reasons for an incomplete structured response."""

    MAX_OUTPUT_TOKENS = "MAX_OUTPUT_TOKENS"
    OTHER = "OTHER"


class ProviderIncomplete(PortModel):
    """Provider response that ended before structured output completed."""

    kind: Literal["INCOMPLETE"]
    reason: IncompleteReason
    duration_ms: int = Field(ge=0)
    request_id: str | None = None


class ProviderErrorCategory(StrEnum):
    """Safe technical categories used by the bounded retry policy."""

    CONNECTION = "CONNECTION"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"
    SERVER = "SERVER"
    AUTHENTICATION = "AUTHENTICATION"
    PERMISSION = "PERMISSION"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    UNKNOWN = "UNKNOWN"


class ProviderFailed(PortModel):
    """Translated provider error without raw exception or applicant content."""

    kind: Literal["FAILED"]
    category: ProviderErrorCategory
    code: str
    duration_ms: int = Field(ge=0)
    request_id: str | None = None


type ExtractionProviderResult = (
    ProviderSucceeded[ApplicationFacts] | ProviderRefused | ProviderIncomplete | ProviderFailed
)
type ParaphraseProviderResult = (
    ProviderSucceeded[ParaphraseDraft] | ProviderRefused | ProviderIncomplete | ProviderFailed
)


class AdmissionsModelPort(Protocol):
    """One-attempt boundary for runtime OpenAI operations."""

    def extract_application_facts(
        self,
        request: ExtractApplicationFactsRequest,
    ) -> ExtractionProviderResult:
        """Attempt one strict bundle-level final-facts extraction."""
        ...

    def paraphrase_summary(self, request: ParaphraseRequest) -> ParaphraseProviderResult:
        """Attempt one optional post-decision paraphrase."""
        ...


class RunIdFactory(Protocol):
    """Private source of operation identifiers."""

    def __call__(self) -> str:
        """Return the next local run identifier."""
        ...

