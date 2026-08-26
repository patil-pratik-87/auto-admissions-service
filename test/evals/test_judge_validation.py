"""Judge calibration: agreement measurement and few-shot leakage guards."""

import pytest

from evals.judges.judge_prompts import JudgePromptExample, build_judge_instructions
from evals.judges.judge_validation import (
    HumanLabel,
    JudgePrediction,
    JudgeType,
    LabelledJudgeCase,
    ValidationSplit,
    measure_judge,
)


def _case(index: int, label: HumanLabel, *, critical: bool = False) -> LabelledJudgeCase:
    return LabelledJudgeCase(
        case_id=f"case-{index}",
        judge=JudgeType.FABRICATED_VALUE,
        split=ValidationSplit.TEST,
        human_label=label,
        critical_false_automatic_eligibility=critical,
    )


def _prediction(index: int, label: HumanLabel) -> JudgePrediction:
    return JudgePrediction(case_id=f"case-{index}", predicted_label=label)


def _example(index: int, label: HumanLabel, *, split: ValidationSplit, borderline: bool) -> JudgePromptExample:
    return JudgePromptExample(
        case_id=f"example-{index}",
        judge=JudgeType.FABRICATED_VALUE,
        split=split,
        human_label=label,
        case_summary="A reported value is checked against the certificate that should state it.",
        critique="The critique names the claim and the page it was checked against.",
        borderline=borderline,
    )


def test_measure_judge_reports_agreement_per_class_rather_than_raw_accuracy() -> None:
    """A judge that passes everything scores well on accuracy and zero on TNR."""
    cases = tuple(_case(index, HumanLabel.PASS) for index in range(9)) + (_case(9, HumanLabel.FAIL),)
    predictions = tuple(_prediction(index, HumanLabel.PASS) for index in range(10))

    metrics = measure_judge(cases=cases, predictions=predictions)

    assert metrics.true_positive_rate == 1.0
    assert metrics.true_negative_rate == 0.0
    assert not metrics.accepted


def test_judge_is_rejected_when_a_critical_case_receives_a_false_pass() -> None:
    """One wrongly blessed automatic eligibility rejects the judge whatever the rates say."""
    cases = tuple(_case(index, HumanLabel.PASS) for index in range(19)) + (
        _case(19, HumanLabel.FAIL, critical=True),
    )
    predictions = tuple(_prediction(index, HumanLabel.PASS) for index in range(20))

    metrics = measure_judge(cases=cases, predictions=predictions)

    assert metrics.critical_false_passes == ("case-19",)
    assert not metrics.accepted


def test_measure_judge_requires_both_classes() -> None:
    """A split with one class cannot produce both rates."""
    cases = tuple(_case(index, HumanLabel.PASS) for index in range(3))
    predictions = tuple(_prediction(index, HumanLabel.PASS) for index in range(3))

    with pytest.raises(ValueError, match="both PASS and FAIL"):
        measure_judge(cases=cases, predictions=predictions)


def test_judge_prompt_rejects_examples_from_the_held_out_split() -> None:
    """Few-shots drawn from TEST would inflate every measurement taken against it."""
    examples = (
        _example(1, HumanLabel.PASS, split=ValidationSplit.TRAIN, borderline=False),
        _example(2, HumanLabel.FAIL, split=ValidationSplit.TEST, borderline=True),
    )

    with pytest.raises(ValueError, match="TRAIN split"):
        build_judge_instructions(JudgeType.FABRICATED_VALUE, examples)


def test_judge_prompt_requires_both_labels_and_a_borderline_example() -> None:
    """A prompt without a boundary case teaches no boundary."""
    examples = (
        _example(1, HumanLabel.PASS, split=ValidationSplit.TRAIN, borderline=False),
        _example(2, HumanLabel.FAIL, split=ValidationSplit.TRAIN, borderline=False),
    )

    with pytest.raises(ValueError, match="borderline"):
        build_judge_instructions(JudgeType.FABRICATED_VALUE, examples)
