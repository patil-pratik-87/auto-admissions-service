"""Frozen outcomes shared by the facts extractor and the rules engine."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.artifacts import ApplicationFactsArtifact
from app.models.failures import ProcessingFailureReport
from app.models.results import ApplicationResult


class ContractModel(BaseModel):
    """Base configuration for immutable, strict module outcomes."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ExtractionSucceeded(ContractModel):
    """Facts extractor outcome containing one complete evaluator artifact."""

    kind: Literal["EXTRACTION_SUCCEEDED"]
    artifact: ApplicationFactsArtifact
    warnings: tuple[str, ...] = ()


class ExtractionFailed(ContractModel):
    """Facts extractor failure with no partial evaluator artifact."""

    kind: Literal["EXTRACTION_FAILED"]
    failure: ProcessingFailureReport
    warnings: tuple[str, ...] = ()


ExtractionOutcome = Annotated[ExtractionSucceeded | ExtractionFailed, Field(discriminator="kind")]


class EvaluationSucceeded(ContractModel):
    """Rules engine outcome containing one deterministic application result."""

    kind: Literal["EVALUATION_SUCCEEDED"]
    result: ApplicationResult


class EvaluationFailed(ContractModel):
    """Rules engine failure with no application result."""

    kind: Literal["EVALUATION_FAILED"]
    failure: ProcessingFailureReport


EvaluationOutcome = Annotated[EvaluationSucceeded | EvaluationFailed, Field(discriminator="kind")]
