import pytest

from app.rules_engine.truth import TruthValue, conjunction, disjunction


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ((TruthValue.TRUE, TruthValue.TRUE), TruthValue.TRUE),
        ((TruthValue.TRUE, TruthValue.UNKNOWN), TruthValue.UNKNOWN),
        ((TruthValue.UNKNOWN, TruthValue.UNKNOWN), TruthValue.UNKNOWN),
        ((TruthValue.FALSE, TruthValue.UNKNOWN), TruthValue.FALSE),
        ((TruthValue.TRUE, TruthValue.FALSE), TruthValue.FALSE),
    ],
)
def test_conjunction_preserves_unknown_without_overriding_proven_false(
    values: tuple[TruthValue, ...],
    expected: TruthValue,
) -> None:
    assert conjunction(values) is expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ((TruthValue.FALSE, TruthValue.FALSE), TruthValue.FALSE),
        ((TruthValue.FALSE, TruthValue.UNKNOWN), TruthValue.UNKNOWN),
        ((TruthValue.UNKNOWN, TruthValue.UNKNOWN), TruthValue.UNKNOWN),
        ((TruthValue.TRUE, TruthValue.UNKNOWN), TruthValue.TRUE),
        ((TruthValue.TRUE, TruthValue.FALSE), TruthValue.TRUE),
    ],
)
def test_disjunction_preserves_unknown_without_overriding_proven_true(
    values: tuple[TruthValue, ...],
    expected: TruthValue,
) -> None:
    assert disjunction(values) is expected
