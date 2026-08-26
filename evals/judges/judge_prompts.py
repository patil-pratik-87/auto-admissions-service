"""Single-purpose prompts for evaluation-only LLM judges."""

from pydantic import BaseModel, ConfigDict

from evals.judges.judge_validation import HumanLabel, JudgeType, ValidationSplit


class EvaluationModel(BaseModel):
    """Base configuration for immutable, strict judge prompt data."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class JudgePromptExample(EvaluationModel):
    """One domain-expert-labelled training example used as a few-shot."""

    case_id: str
    judge: JudgeType
    split: ValidationSplit
    human_label: HumanLabel
    case_summary: str
    critique: str
    borderline: bool


_CRITERIA: dict[JudgeType, tuple[str, str, str]] = {
    JudgeType.FABRICATED_VALUE: (
        "Assess only whether every value the extractor reported as KNOWN actually appears in the supplied "
        "applicant documents.",
        "every KNOWN value appears in the documents, either stated outright or following from stated content by "
        "reading dates, totals, or a printed heading.",
        "any KNOWN value is absent from the documents or contradicts them, including qualification type, country, "
        "completion, dates, durations, weekly hours, and restriction codes.",
    ),
    JudgeType.OMITTED_EVIDENCE: (
        "Assess only whether a field the extracted facts already define was left empty when the documents state it "
        "legibly. The facts use a closed schema, so information with no field in the supplied facts is out of scope "
        "and is never an omission. Do not judge whether an omission would change the outcome; the rules engine "
        "settles that.",
        "every field present in the extracted facts is filled from the documents wherever they state it legibly.",
        "a field present in the extracted facts was left empty, or recorded as MISSING, while a document states it "
        "legibly, such as a territorial restriction, a completion date, or an employment period.",
    ),
    JudgeType.EVIDENCE_STATE: (
        "Assess only whether each fact carries the correct evidence state of KNOWN, MISSING, UNREADABLE, or "
        "CONFLICTING, given what the documents show.",
        "KNOWN is used only where the value is legible and unambiguous, UNREADABLE where the field is present but "
        "cannot be read, MISSING where no document addresses the field, and CONFLICTING where two documents state "
        "values that cannot both hold.",
        "any state stands in for another, including KNOWN over an illegible field, KNOWN where two documents "
        "disagree, or MISSING where the field is present but unreadable.",
    ),
}


def build_judge_instructions(judge: JudgeType, examples: tuple[JudgePromptExample, ...]) -> str:
    """Build one calibrated binary judge prompt from training examples only.

    Args:
        judge: The single semantic failure mode assessed by the prompt.
        examples: Two to four domain-expert-labelled examples from the training split.

    Returns:
        Complete task, definitions, few-shot examples, and structured-output instructions.

    Raises:
        ValueError: If examples leak held-out data or do not cover the decision boundary.
    """
    if not 2 <= len(examples) <= 4:
        raise ValueError("Judge prompts require two to four TRAIN examples")
    if any(example.split is not ValidationSplit.TRAIN for example in examples):
        raise ValueError("Judge prompt examples must come only from the TRAIN split")
    if any(example.judge is not judge for example in examples):
        raise ValueError("Judge prompt examples must match the requested judge")
    labels = {example.human_label for example in examples}
    if labels != {HumanLabel.PASS, HumanLabel.FAIL}:
        raise ValueError("Judge prompt examples must include PASS and FAIL")
    if not any(example.borderline for example in examples):
        raise ValueError("Judge prompt examples must include a borderline case")

    task, pass_definition, fail_definition = _CRITERIA[judge]
    example_sections = []
    for index, example in enumerate(examples, start=1):
        example_sections.append(
            "\n".join(
                (
                    f"### Example {index}: {example.human_label.value}{' (borderline)' if example.borderline else ''}",
                    f"Case: {example.case_summary}",
                    f"Critique: {example.critique}",
                    f"Result: {example.human_label.value}",
                )
            )
        )

    return "\n\n".join(
        (
            "# Task and evaluation criterion\n"
            "You are an evaluation-only reviewer of synthetic admissions cases. "
            f"{task} Do not make or change an admissions decision.",
            "# PASS and FAIL definitions\n"
            f"PASS: {pass_definition}\n"
            f"FAIL: {fail_definition}\n\n"
            "Do not recalculate policy thresholds, interpret the policy DSL, validate JSON schemas or identifiers, "
            "check exact local citation matching, or claim document authenticity. Those checks are deterministic or "
            "external. Judge only the criterion above.",
            "# Human-labelled training examples\n" + "\n\n".join(example_sections),
            "# Structured output\n"
            "Return the detailed critique before the binary result. Identify concrete affected claims and one-based "
            "document/page pointers. The schema-enforced result must be exactly PASS or FAIL; do not use a score, "
            "partial credit, or an uncertain label.",
        )
    )
