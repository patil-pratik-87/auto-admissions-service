"""Three-valued truth operations owned by the admissions rules engine."""

from enum import StrEnum


class TruthValue(StrEnum):
    """Result of evaluating one evidence-aware policy expression."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


def conjunction(values: tuple[TruthValue, ...]) -> TruthValue:
    """Compose a non-empty conjunction using Kleene-style semantics."""
    if not values:
        raise ValueError("A conjunction must contain at least one value")
    if TruthValue.FALSE in values:
        return TruthValue.FALSE
    if all(value is TruthValue.TRUE for value in values):
        return TruthValue.TRUE
    return TruthValue.UNKNOWN


def disjunction(values: tuple[TruthValue, ...]) -> TruthValue:
    """Compose a non-empty disjunction using Kleene-style semantics."""
    if not values:
        raise ValueError("A disjunction must contain at least one value")
    if TruthValue.TRUE in values:
        return TruthValue.TRUE
    if all(value is TruthValue.FALSE for value in values):
        return TruthValue.FALSE
    return TruthValue.UNKNOWN
