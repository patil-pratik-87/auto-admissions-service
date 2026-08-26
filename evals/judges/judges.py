"""Evaluation-only LLM judge contracts and provider port."""

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.models.facts import ApplicationFacts
from app.models.results import ApplicationResult
from evals.judges.judge_validation import HumanLabel, JudgeType


class EvaluationModel(BaseModel):
    """Base configuration for immutable, strict judge contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class JudgePagePointer(EvaluationModel):
    """One-based location cited in a judge critique."""

    document_number: int = Field(ge=1)
    page_number: int = Field(ge=1)


class JudgeVerdict(EvaluationModel):
    """Detailed critique followed by one calibrated binary verdict."""

    critique: str = Field(min_length=20)
    affected_claims: tuple[str, ...]
    affected_pages: tuple[JudgePagePointer, ...]
    result: HumanLabel


class JudgeRequest(EvaluationModel):
    """Approved synthetic documents, extracted facts, and result for one judge."""

    fixture_id: str
    judge: JudgeType
    pdf_paths: tuple[Path, ...]
    facts: ApplicationFacts
    result: ApplicationResult
    instructions: str
    model: str
    prompt_version: str
    schema_version: Literal["1.0"] = "1.0"
    max_output_tokens: int = Field(gt=0)


class JudgeUsage(EvaluationModel):
    """Token accounting returned by one live judge attempt."""

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class JudgeSucceeded(EvaluationModel):
    """Completed strict judge verdict for one synthetic fixture."""

    kind: Literal["SUCCEEDED"]
    verdict: JudgeVerdict
    model_returned: str
    usage: JudgeUsage
    duration_ms: int = Field(ge=0)


class JudgeFailureCategory(StrEnum):
    """Evaluation-only failure category that never becomes an applicant result."""

    REFUSAL = "REFUSAL"
    INCOMPLETE = "INCOMPLETE"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    PROVIDER = "PROVIDER"


class JudgeFailed(EvaluationModel):
    """Safe judge failure without an invented PASS or FAIL verdict."""

    kind: Literal["FAILED"]
    category: JudgeFailureCategory
    code: str
    retryable: bool
    duration_ms: int = Field(ge=0)


JudgeProviderResult = Annotated[JudgeSucceeded | JudgeFailed, Field(discriminator="kind")]


class JudgeModelPort(Protocol):
    """Separate provider boundary that runtime admissions code never imports."""

    def evaluate(self, request: JudgeRequest) -> JudgeProviderResult:
        """Evaluate one synthetic case against one semantic criterion."""
        ...
