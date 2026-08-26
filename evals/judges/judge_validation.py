"""Binary judge types and the agreement measurement that calibrates one against human labels."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class EvaluationModel(BaseModel):
    """Base configuration for immutable, strict evaluation contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class JudgeType(StrEnum):
    """One judge per way extraction fails: too much, too little, wrong uncertainty."""

    FABRICATED_VALUE = "FABRICATED_VALUE"
    OMITTED_EVIDENCE = "OMITTED_EVIDENCE"
    EVIDENCE_STATE = "EVIDENCE_STATE"


class HumanLabel(StrEnum):
    """Binary domain-expert label used as judge ground truth."""

    PASS = "PASS"
    FAIL = "FAIL"


class ValidationSplit(StrEnum):
    """Disjoint splits. TRAIN supplies few-shots, TEST measures the judge."""

    TRAIN = "TRAIN"
    TEST = "TEST"


class LabelledJudgeCase(EvaluationModel):
    """One domain-expert label for one screened application."""

    case_id: str
    judge: JudgeType
    split: ValidationSplit
    human_label: HumanLabel
    critical_false_automatic_eligibility: bool = False


class JudgePrediction(EvaluationModel):
    """Binary judge output associated with one labelled case."""

    case_id: str
    predicted_label: HumanLabel


class JudgeMetrics(EvaluationModel):
    """Agreement with human labels, plus the zero-tolerance safety result."""

    true_positives: int
    false_negatives: int
    true_negatives: int
    false_positives: int
    true_positive_rate: float
    true_negative_rate: float
    critical_false_passes: tuple[str, ...]
    accepted: bool


def measure_judge(
    *,
    cases: tuple[LabelledJudgeCase, ...],
    predictions: tuple[JudgePrediction, ...],
    minimum_true_positive_rate: float = 0.90,
    minimum_true_negative_rate: float = 0.90,
) -> JudgeMetrics:
    """Measure one judge against one human-labelled split.

    TPR is agreement on human PASS labels and TNR is agreement on human FAIL labels.
    Raw accuracy is not reported, because a judge that always says PASS scores well on it
    while catching nothing. A single false PASS on a case flagged as a critical automatic
    eligibility rejects the judge outright, whatever the rates say.

    Args:
        cases: Domain-expert labels from one judge and one split.
        predictions: Judge predictions with exactly the same case identifiers.
        minimum_true_positive_rate: Required agreement on human PASS labels.
        minimum_true_negative_rate: Required agreement on human FAIL labels.

    Returns:
        Confusion counts, both rates, critical false passes, and acceptance.

    Raises:
        ValueError: If inputs are empty, mixed, duplicated, or incomplete.
    """
    if not cases:
        raise ValueError("Judge measurement requires labelled cases")
    if len({case.judge for case in cases}) != 1 or len({case.split for case in cases}) != 1:
        raise ValueError("Judge measurement requires one judge and one split")

    cases_by_id = {case.case_id: case for case in cases}
    predictions_by_id = {prediction.case_id: prediction for prediction in predictions}
    if len(cases_by_id) != len(cases) or len(predictions_by_id) != len(predictions):
        raise ValueError("Case identifiers must be unique")
    if cases_by_id.keys() != predictions_by_id.keys():
        raise ValueError("Predictions must match every labelled case exactly")

    true_positives = 0
    false_negatives = 0
    true_negatives = 0
    false_positives = 0
    critical_false_passes: list[str] = []

    for case_id in sorted(cases_by_id):
        case = cases_by_id[case_id]
        predicted = predictions_by_id[case_id].predicted_label
        if case.human_label is HumanLabel.PASS:
            if predicted is HumanLabel.PASS:
                true_positives += 1
            else:
                false_negatives += 1
        elif predicted is HumanLabel.FAIL:
            true_negatives += 1
        else:
            false_positives += 1
            if case.critical_false_automatic_eligibility:
                critical_false_passes.append(case_id)

    positive_total = true_positives + false_negatives
    negative_total = true_negatives + false_positives
    if positive_total == 0 or negative_total == 0:
        raise ValueError("Judge measurement requires both PASS and FAIL human labels")

    true_positive_rate = true_positives / positive_total
    true_negative_rate = true_negatives / negative_total
    return JudgeMetrics(
        true_positives=true_positives,
        false_negatives=false_negatives,
        true_negatives=true_negatives,
        false_positives=false_positives,
        true_positive_rate=true_positive_rate,
        true_negative_rate=true_negative_rate,
        critical_false_passes=tuple(critical_false_passes),
        accepted=(
            true_positive_rate >= minimum_true_positive_rate
            and true_negative_rate >= minimum_true_negative_rate
            and not critical_false_passes
        ),
    )
