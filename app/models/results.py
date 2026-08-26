"""Evidence-backed academic-access application result contracts."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, JsonValue, model_validator

from app.models.programs import PolicyRef


class ContractModel(BaseModel):
    """Base configuration for immutable, strict application result contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class RuleId(StrEnum):
    """Admissions rules configured by the active Bachelor policy."""

    GERMAN_ABITUR = "GERMAN_ABITUR"
    FACHGEBUNDENE_HOCHSCHULREIFE = "FACHGEBUNDENE_HOCHSCHULREIFE"
    GERMAN_GENERAL_FACHHOCHSCHULREIFE = "GERMAN_GENERAL_FACHHOCHSCHULREIFE"
    GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL = "GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL"
    GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE = "GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE"


RULE_ORDER = tuple(RuleId)


class RuleStatus(StrEnum):
    """Public result of evaluating one configured admissions rule."""

    ELIGIBLE = "ELIGIBLE"
    CONDITIONALLY_ELIGIBLE = "CONDITIONALLY_ELIGIBLE"
    NOT_SATISFIED = "NOT_SATISFIED"
    MISSING_INFORMATION = "MISSING_INFORMATION"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ApplicationStatus(StrEnum):
    """Final academic-access result after rule resolution."""

    ELIGIBLE = "ELIGIBLE"
    CONDITIONALLY_ELIGIBLE = "CONDITIONALLY_ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    MISSING_INFORMATION = "MISSING_INFORMATION"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class ProgramRef(ContractModel):
    """Selected study program shown in an application result."""

    id: str
    display_name: str


class EvidencePointer(ContractModel):
    """Decision-relevant source location exposed to the local reviewer."""

    evidence_id: str
    document_id: str
    page_number: int
    excerpt: str | None


class EntryCondition(ContractModel):
    """Machine-readable entry condition copied from the active policy."""

    id: str
    parameters: dict[str, JsonValue]


class RuleResult(ContractModel):
    """Deterministic outcome for one configured admissions rule."""

    rule_id: RuleId
    status: RuleStatus
    reason_code: str
    candidate_ids: tuple[str, ...]
    fact_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    condition: EntryCondition | None


class MissingInformationItem(ContractModel):
    """One unknown fact that affects one or more rule results."""

    fact_id: str
    label: str
    state: Literal["MISSING", "UNREADABLE", "CONFLICTING"]
    rule_ids: tuple[RuleId, ...]
    evidence_ids: tuple[str, ...]


class ManualReviewItem(ContractModel):
    """One stable explanation of why human review is required."""

    reason_code: str
    explanation: str
    rule_ids: tuple[RuleId, ...]
    evidence_ids: tuple[str, ...]


class CanonicalSummary(ContractModel):
    """Required deterministic human-readable result explanation."""

    headline: str
    explanation: str
    required_information: tuple[str, ...]


class ResultSummary(ContractModel):
    """Canonical summary plus optional post-decision paraphrase."""

    canonical: CanonicalSummary
    llm_paraphrase: str | None


class ApplicationResult(ContractModel):
    """Complete local result of deterministic academic-access evaluation."""

    kind: Literal["APPLICATION_RESULT"]
    result_version: Literal["2.0"]
    run_id: str
    scope: Literal["ACADEMIC_ACCESS_ONLY"]
    program: ProgramRef
    policy: PolicyRef
    application_status: ApplicationStatus
    application_reason_code: str
    rules: tuple[RuleResult, ...]
    missing_information: tuple[MissingInformationItem, ...]
    manual_review: tuple[ManualReviewItem, ...]
    warnings: tuple[str, ...]
    evidence: tuple[EvidencePointer, ...]
    summary: ResultSummary

    @model_validator(mode="after")
    def contains_every_rule_in_canonical_order(self) -> Self:
        """Keep every supported rule explicit and serialized deterministically."""
        rule_ids = tuple(rule.rule_id for rule in self.rules)
        if rule_ids != RULE_ORDER:
            expected = ", ".join(rule.value for rule in RULE_ORDER)
            raise ValueError(f"rules must contain the canonical order: {expected}")
        return self
