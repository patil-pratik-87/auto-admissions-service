"""Immutable internal representation of one activated admissions policy."""

from dataclasses import dataclass
from typing import Any, Literal, Protocol

from app.models.results import ApplicationStatus, EntryCondition, RuleId, RuleStatus


class Comparison(Protocol):
    """Opaque compiled scalar comparison evaluated only with known values."""

    def matches(self, actual: object) -> bool:
        """Compare one known scalar against the compiler-owned expected value."""
        ...


@dataclass(frozen=True, slots=True)
class AtomicExpression:
    """One evidence-gated scalar comparison."""

    comparison_id: str
    fact_path: str
    operator: Literal["eq", "in", "gte", "lt"]
    expected: Any
    comparison: Comparison


@dataclass(frozen=True, slots=True)
class AllExpression:
    """Three-valued conjunction."""

    children: tuple["Expression", ...]


@dataclass(frozen=True, slots=True)
class AnyExpression:
    """Three-valued disjunction."""

    children: tuple["Expression", ...]


type Expression = AtomicExpression | AllExpression | AnyExpression


@dataclass(frozen=True, slots=True)
class ResultDefinition:
    """Configured result selected by deterministic control flow."""

    status: RuleStatus
    reason_code: str
    condition: EntryCondition | None = None


@dataclass(frozen=True, slots=True)
class ApplicabilityDefinition:
    """Applicability expression and its explicit false and unknown results."""

    expression: Expression
    not_applicable: ResultDefinition
    unknown: ResultDefinition


@dataclass(frozen=True, slots=True)
class RequirementDefinition:
    """Requirement expression and its true, false, and unknown results."""

    expression: Expression
    satisfied: ResultDefinition
    not_satisfied: ResultDefinition
    unknown: ResultDefinition


@dataclass(frozen=True, slots=True)
class BranchDefinition:
    """One ordered branch condition and result."""

    when: Expression
    result: ResultDefinition


@dataclass(frozen=True, slots=True)
class BranchGroupDefinition:
    """First-non-false branch group with explicit safe fallbacks."""

    first_match: tuple[BranchDefinition, ...]
    unknown: ResultDefinition
    otherwise: ResultDefinition


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    """One compiled candidate-scoped admissions rule."""

    rule_id: RuleId
    source: Literal[
        "school_qualifications",
        "advanced_vocational_qualifications",
        "professional_access_candidates",
    ]
    alias: Literal["qualification", "candidate"]
    selector: Expression
    applicability: ApplicabilityDefinition | None
    requirement: RequirementDefinition | None
    branches: BranchGroupDefinition | None


@dataclass(frozen=True, slots=True)
class ResolutionDefinition:
    """One ordered application-resolution case."""

    kind: Literal["ANY_RULE", "ALL_APPLICABLE", "NO_RECOGNIZED_RULE"]
    rule_status: RuleStatus | None
    application_status: ApplicationStatus


@dataclass(frozen=True, slots=True)
class CompiledPolicy:
    """Complete immutable activated policy used by RulesEngine."""

    policy_id: str
    version: str
    applies_when: Expression
    rules: tuple[RuleDefinition, ...]
    resolution: tuple[ResolutionDefinition, ...]
