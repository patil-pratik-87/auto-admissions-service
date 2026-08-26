"""Public synchronous interface for admissions screening operations."""

from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.artifacts import ApplicationFactsArtifact
from app.models.failures import ProcessingFailureReport
from app.models.results import ApplicationResult


class InterfaceModel(BaseModel):
    """Base configuration for immutable, strict interface contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ExtractRequest(InterfaceModel):
    """Request strict model-extracted facts from one complete PDF bundle."""

    program_id: str
    pdf_paths: tuple[Path, ...] = Field(min_length=1)
    output_path: Path
    model: str | None = None
    overwrite: bool = False


class EvaluateRequest(InterfaceModel):
    """Request deterministic evaluation of one saved facts artifact."""

    facts_path: Path
    output_path: Path
    paraphrase: bool = False
    overwrite: bool = False


class ScreenRequest(InterfaceModel):
    """Request extraction followed by exact-artifact deterministic evaluation."""

    program_id: str
    pdf_paths: tuple[Path, ...] = Field(min_length=1)
    output_dir: Path
    model: str | None = None
    paraphrase: bool = False
    overwrite: bool = False


class SafeProgressEvent(InterfaceModel):
    """Applicant-free progress information suitable for terminal display."""

    stage: str
    message: str
    current: int | None = Field(default=None, ge=0)
    total: int | None = Field(default=None, ge=0)


ProgressSink = Callable[[SafeProgressEvent], None]


def null_progress(_: SafeProgressEvent) -> None:
    """Ignore a safe progress event."""


class ExtractCompleted(InterfaceModel):
    """Successful extraction outcome and exact saved artifact path."""

    kind: Literal["EXTRACT_COMPLETED"]
    artifact: ApplicationFactsArtifact
    facts_path: Path
    warnings: tuple[str, ...] = ()


class EvaluateCompleted(InterfaceModel):
    """Successful evaluation outcome and exact saved result path."""

    kind: Literal["EVALUATE_COMPLETED"]
    result: ApplicationResult
    result_path: Path
    warnings: tuple[str, ...] = ()


class ScreenCompleted(InterfaceModel):
    """Successful end-to-end outcome with both persistence boundaries."""

    kind: Literal["SCREEN_COMPLETED"]
    artifact: ApplicationFactsArtifact
    result: ApplicationResult
    facts_path: Path
    result_path: Path
    warnings: tuple[str, ...] = ()


class RunFailed(InterfaceModel):
    """Expected workflow failure returned without an applicant outcome."""

    kind: Literal["RUN_FAILED"]
    operation: Literal["EXTRACT", "EVALUATE", "SCREEN"]
    failure: ProcessingFailureReport
    failure_path: Path | None = None
    retained_facts_path: Path | None = None
    warnings: tuple[str, ...] = ()
