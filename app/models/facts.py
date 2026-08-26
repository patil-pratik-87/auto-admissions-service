"""Strict application facts returned directly by structured extraction."""

from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    """Base configuration for immutable, strict fact contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceRef(ContractModel):
    """LLM-reported source pointer used only for explanation."""

    document_id: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    excerpt: str | None = None


class CandidateValue[T](ContractModel):
    """One typed value reported inside a factual conflict."""

    value: T
    evidence: tuple[EvidenceRef, ...] = ()


class KnownFact[T](ContractModel):
    """A typed value that the extraction model reports as known."""

    state: Literal["KNOWN"]
    fact_id: str = Field(min_length=1)
    value: T
    evidence: tuple[EvidenceRef, ...] = ()


class MissingFact(ContractModel):
    """A policy-relevant value that the extraction model did not find."""

    state: Literal["MISSING"]
    fact_id: str = Field(min_length=1)
    evidence: tuple[EvidenceRef, ...] = ()


class UnreadableFact(ContractModel):
    """A reported source location whose relevant value is unreadable."""

    state: Literal["UNREADABLE"]
    fact_id: str = Field(min_length=1)
    evidence: tuple[EvidenceRef, ...] = Field(min_length=1)


class ConflictingFact[T](ContractModel):
    """Two or more distinct typed values reported for one fact."""

    state: Literal["CONFLICTING"]
    fact_id: str = Field(min_length=1)
    candidates: tuple[CandidateValue[T], ...] = Field(min_length=2)

    @model_validator(mode="after")
    def candidate_values_are_distinct(self) -> Self:
        """Reject repeated values that do not form a structural conflict."""
        for index, candidate in enumerate(self.candidates):
            if any(candidate.value == earlier.value for earlier in self.candidates[:index]):
                raise ValueError("A conflicting fact requires distinct values")
        return self


type Fact[T] = KnownFact[T] | MissingFact | UnreadableFact | ConflictingFact[T]
type AnyFact = KnownFact[Any] | MissingFact | UnreadableFact | ConflictingFact[Any]


NonNegativeInt = Annotated[int, Field(ge=0)]
DqrOrEqrLevel = Annotated[int, Field(ge=1, le=8)]


class SchoolQualificationType(StrEnum):
    """School qualification categories consumed by the active policy."""

    ALLGEMEINE_HOCHSCHULREIFE = "ALLGEMEINE_HOCHSCHULREIFE"
    FACHGEBUNDENE_HOCHSCHULREIFE = "FACHGEBUNDENE_HOCHSCHULREIFE"
    FACHHOCHSCHULREIFE = "FACHHOCHSCHULREIFE"
    OTHER = "OTHER"


class AdvancedVocationalType(StrEnum):
    """Advanced vocational categories consumed by the active policy."""

    MEISTER = "MEISTER"
    ADVANCED_VOCATIONAL = "ADVANCED_VOCATIONAL"
    OTHER = "OTHER"


class VocationalTrainingType(StrEnum):
    """Vocational training categories consumed by the active policy."""

    VOCATIONAL_TRAINING = "VOCATIONAL_TRAINING"
    OTHER = "OTHER"


class AccessScope(StrEnum):
    """Academic scope reported for a school qualification."""

    GENERAL = "GENERAL"
    SUBJECT_RESTRICTED = "SUBJECT_RESTRICTED"
    OTHER = "OTHER"


class ValidityRestrictionCode(StrEnum):
    """Territorial restrictions recognized by the active policy."""

    ALL_GERMAN_STATES = "ALL_GERMAN_STATES"
    THURINGIA = "THURINGIA"
    ALL_STATES_EXCEPT_BAVARIA_AND_SAXONY = "ALL_STATES_EXCEPT_BAVARIA_AND_SAXONY"
    OTHER = "OTHER"


class IssuingRegion(StrEnum):
    """Region grouping used by the subject-restricted school rule."""

    DACH = "DACH"
    OUTSIDE_DACH = "OUTSIDE_DACH"


class SubjectRelationship(StrEnum):
    """Relationship between professional evidence and the selected subject."""

    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNCERTAIN = "UNCERTAIN"


class SchoolQualification(ContractModel):
    """One final evaluator-facing school qualification."""

    qualification_id: str = Field(min_length=1)
    type: Fact[SchoolQualificationType]
    country: Fact[str] = Field(
        description="Issuing country as an ISO 3166-1 alpha-2 code, for example DE for Germany."
    )
    completed: Fact[bool]
    access_scope: Fact[AccessScope] = Field(
        description=(
            "Whether the qualification restricts which subjects the holder may "
            "study. GENERAL: no subject restriction is stated. SUBJECT_RESTRICTED: "
            "the document limits access to a named subject or field of study, as a "
            "fachgebundene Hochschulreife does. A limit on the type of institution "
            "is not a subject restriction: a Fachhochschulreife that grants access "
            "to Fachhochschulen without naming a subject is GENERAL."
        )
    )
    validity_restriction_present: Fact[bool]
    validity_restriction_code: Fact[ValidityRestrictionCode]
    school_part_proven: Fact[bool]
    vocational_part_proven: Fact[bool]
    issuing_region: Fact[IssuingRegion]


class AdvancedVocationalQualification(ContractModel):
    """One final evaluator-facing advanced vocational qualification."""

    qualification_id: str = Field(min_length=1)
    type: Fact[AdvancedVocationalType]
    country: Fact[str] = Field(
        description="Issuing country as an ISO 3166-1 alpha-2 code, for example DE for Germany."
    )
    completed: Fact[bool]
    dqr_or_eqr_level: Fact[DqrOrEqrLevel]
    teaching_hours: Fact[NonNegativeInt]
    builds_on_completed_training: Fact[bool]
    builds_on_recognized_training: Fact[bool]


class VocationalTraining(ContractModel):
    """Training facts nested under one professional-access candidate."""

    training_id: str = Field(min_length=1)
    type: Fact[VocationalTrainingType]
    country: Fact[str] = Field(
        description="Issuing country as an ISO 3166-1 alpha-2 code, for example DE for Germany."
    )
    completed: Fact[bool]
    recognized: Fact[bool]
    duration_months: Fact[NonNegativeInt]
    dqr_or_eqr_level: Fact[DqrOrEqrLevel]
    subject: Fact[str]


class ProfessionalAccessCandidate(ContractModel):
    """One complete candidate-scoped professional-access interpretation."""

    candidate_id: str = Field(min_length=1)
    training: VocationalTraining
    employment_period_ids: tuple[str, ...] = ()
    all_period_dates_known: Fact[bool]
    all_weekly_hours_known: Fact[bool]
    mini_job_classification_complete: Fact[bool]
    full_time_equivalent_days_after_training: Fact[NonNegativeInt]
    professional_fields_after_training: Fact[tuple[str, ...]]
    subject_relationship: Fact[SubjectRelationship]

    @model_validator(mode="after")
    def employment_period_ids_are_unique(self) -> Self:
        """Prevent ambiguous explanatory links inside one candidate."""
        if len(self.employment_period_ids) != len(set(self.employment_period_ids)):
            raise ValueError("employment period identifiers must be unique within a candidate")
        return self


def _school_facts(qualification: SchoolQualification) -> tuple[AnyFact, ...]:
    return (
        qualification.type,
        qualification.country,
        qualification.completed,
        qualification.access_scope,
        qualification.validity_restriction_present,
        qualification.validity_restriction_code,
        qualification.school_part_proven,
        qualification.vocational_part_proven,
        qualification.issuing_region,
    )


def _advanced_facts(qualification: AdvancedVocationalQualification) -> tuple[AnyFact, ...]:
    return (
        qualification.type,
        qualification.country,
        qualification.completed,
        qualification.dqr_or_eqr_level,
        qualification.teaching_hours,
        qualification.builds_on_completed_training,
        qualification.builds_on_recognized_training,
    )


def _training_facts(training: VocationalTraining) -> tuple[AnyFact, ...]:
    return (
        training.type,
        training.country,
        training.completed,
        training.recognized,
        training.duration_months,
        training.dqr_or_eqr_level,
        training.subject,
    )


def _candidate_facts(candidate: ProfessionalAccessCandidate) -> tuple[AnyFact, ...]:
    return (
        *_training_facts(candidate.training),
        candidate.all_period_dates_known,
        candidate.all_weekly_hours_known,
        candidate.mini_job_classification_complete,
        candidate.full_time_equivalent_days_after_training,
        candidate.professional_fields_after_training,
        candidate.subject_relationship,
    )


class ApplicationFacts(ContractModel):
    """Complete strict evaluator input returned by one extraction call."""

    schema_version: Literal["2.0"]
    school_qualifications: tuple[SchoolQualification, ...]
    advanced_vocational_qualifications: tuple[AdvancedVocationalQualification, ...]
    professional_access_candidates: tuple[ProfessionalAccessCandidate, ...]

    @model_validator(mode="after")
    def identifiers_are_unique(self) -> Self:
        """Keep deterministic selectors and report links unambiguous."""
        school_ids = tuple(item.qualification_id for item in self.school_qualifications)
        advanced_ids = tuple(item.qualification_id for item in self.advanced_vocational_qualifications)
        candidate_ids = tuple(item.candidate_id for item in self.professional_access_candidates)
        training_ids = tuple(item.training.training_id for item in self.professional_access_candidates)

        for label, identifiers in (
            ("school qualification", school_ids),
            ("advanced vocational qualification", advanced_ids),
            ("professional access candidate", candidate_ids),
            ("vocational training", training_ids),
        ):
            if len(identifiers) != len(set(identifiers)):
                raise ValueError(f"{label} identifiers must be unique")

        facts = (
            *(fact for item in self.school_qualifications for fact in _school_facts(item)),
            *(fact for item in self.advanced_vocational_qualifications for fact in _advanced_facts(item)),
            *(fact for item in self.professional_access_candidates for fact in _candidate_facts(item)),
        )
        fact_ids = tuple(fact.fact_id for fact in facts)
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("fact identifiers must be unique")
        return self
