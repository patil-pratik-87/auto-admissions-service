"""Restricted zeroSteiner scalar comparison compilation."""

from dataclasses import dataclass
from decimal import Context
from enum import StrEnum
from typing import Any, Literal

import rule_engine as zerosteiner

from app.rules_engine.errors import PolicyActivationError

Operator = Literal["eq", "in", "gte", "lt"]

_EXPRESSIONS: dict[Operator, str] = {
    "eq": "actual == expected",
    "in": "actual in expected",
    "gte": "actual >= expected",
    "lt": "actual < expected",
}


def _native(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return tuple(_native(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class ZeroSteinerComparison:
    """One eagerly compiled comparison with a fixed expected binding."""

    expression: zerosteiner.Rule
    expected: Any

    def matches(self, actual: object) -> bool:
        """Evaluate one known native value without exposing fact wrappers."""
        return bool(self.expression.matches({"actual": _native(actual), "expected": self.expected}))


def compile_comparison(operator: Operator, expected: Any) -> ZeroSteinerComparison:
    """Compile one allowlisted typed binary comparison."""
    native_expected = _native(expected)
    if operator == "in" and not isinstance(native_expected, tuple):
        raise PolicyActivationError("INVALID_COMPARISON", "Membership comparisons require a non-empty tuple")
    if operator == "in" and not native_expected:
        raise PolicyActivationError("INVALID_COMPARISON", "Membership comparisons require a non-empty tuple")

    representative_actual = native_expected[0] if operator == "in" else native_expected
    try:
        context = zerosteiner.Context(
            type_resolver={"actual": representative_actual, "expected": native_expected},
            default_timezone="utc",
            decimal_context=Context(prec=28),
            mapping_attribute_lookup=False,
        )
        expression = zerosteiner.Rule(_EXPRESSIONS[operator], context=context)
    except (TypeError, ValueError, zerosteiner.errors.EngineError) as error:
        raise PolicyActivationError("INVALID_COMPARISON", "A policy comparison could not be compiled") from error

    if context.symbols != {"actual", "expected"}:
        raise PolicyActivationError("UNSAFE_COMPARISON", "A policy comparison contains unsupported symbols")
    return ZeroSteinerComparison(expression=expression, expected=native_expected)
