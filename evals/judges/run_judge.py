"""Run one judge over one screened application through the real OpenAI adapter.

The few-shot examples below stand in for domain-expert labels, which do not exist yet, so a
verdict from this script is a demonstration rather than a measurement. A judge counts only
after `measure_judge` scores it against real labels on the held-out split.

Usage:
    uv run python -m evals.judges.run_judge <run-dir> --pdf <file.pdf> [--judge EVIDENCE_STATE]

    where <run-dir> holds application-facts.json and application-result.json, as written by
    `admissions screen --output-dir`.
"""

import argparse
import json
import os
from pathlib import Path

from langsmith.wrappers import wrap_openai
from openai import OpenAI

from app.bootstrap import AdmissionsSettings
from app.models.artifacts import ApplicationFactsArtifact
from app.models.results import ApplicationResult
from evals.judges.judge_prompts import JudgePromptExample, build_judge_instructions
from evals.judges.judge_validation import HumanLabel, JudgeType, ValidationSplit
from evals.judges.judges import JudgeProviderResult, JudgeRequest, JudgeSucceeded
from evals.judges.openai_judge import OpenAIJudgeAdapter

JUDGE_PROJECT = os.getenv("JUDGE_LANGSMITH_PROJECT", "auto-admissions-judges")


def build_judge_client(settings: AdmissionsSettings) -> OpenAI:
    """An OpenAI client for judging, traced to its own LangSmith project when a key is set.

    Judge traces go to a project separate from screening, so a judge call is never mistaken
    for a decision the applicant received.
    """
    assert settings.openai_api_key is not None
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value(), max_retries=0)
    langsmith_key = settings.langsmith_key_value
    if langsmith_key is None:
        return client
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_key
    os.environ["LANGSMITH_PROJECT"] = JUDGE_PROJECT
    if settings.langsmith_endpoint is not None:
        os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    return wrap_openai(client)


def save_verdict(
    output_dir: Path, fixture_id: str, judge: JudgeType, model: str, outcome: JudgeProviderResult
) -> Path:
    """Write one judge outcome next to the screening artifacts it judged."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"judge-{judge.value.lower().replace('_', '-')}.json"
    record: dict[str, object] = {"fixture_id": fixture_id, "judge": judge.value, "model": model}
    if isinstance(outcome, JudgeSucceeded):
        record |= {
            "result": outcome.verdict.result.value,
            "critique": outcome.verdict.critique,
            "affected_claims": list(outcome.verdict.affected_claims),
            "affected_pages": [[p.document_number, p.page_number] for p in outcome.verdict.affected_pages],
            "model_returned": outcome.model_returned,
            "input_tokens": outcome.usage.input_tokens,
            "output_tokens": outcome.usage.output_tokens,
            "duration_ms": outcome.duration_ms,
        }
    else:
        record |= {"result": "ERROR", "category": str(outcome.category), "code": outcome.code}
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path


def _example(
    case_id: str,
    judge: JudgeType,
    label: HumanLabel,
    case_summary: str,
    critique: str,
    *,
    borderline: bool = False,
) -> JudgePromptExample:
    """Build one TRAIN few-shot example."""
    return JudgePromptExample(
        case_id=case_id,
        judge=judge,
        split=ValidationSplit.TRAIN,
        human_label=label,
        case_summary=case_summary,
        critique=critique,
        borderline=borderline,
    )


EXAMPLES: dict[JudgeType, tuple[JudgePromptExample, ...]] = {
    JudgeType.FABRICATED_VALUE: (
        _example(
            "fab-pass", JudgeType.FABRICATED_VALUE, HumanLabel.PASS,
            "type is ALLGEMEINE_HOCHSCHULREIFE and page 1 is headed 'Zeugnis der Allgemeinen Hochschulreife'.",
            "The heading states the qualification type outright, so the KNOWN value appears in the document.",
        ),
        _example(
            "fab-fail", JudgeType.FABRICATED_VALUE, HumanLabel.FAIL,
            "validity_restriction_code is ALL_GERMAN_STATES and no page names a scope.",
            "No document states a national scope. The extractor supplied a default rather than a read value.",
        ),
        _example(
            "fab-borderline", JudgeType.FABRICATED_VALUE, HumanLabel.PASS,
            "employment months is 30 and the certificate prints only a start and an end date.",
            "The total is not printed, and it follows from two printed dates, so the value is read rather than "
            "invented.",
            borderline=True,
        ),
    ),
    JudgeType.OMITTED_EVIDENCE: (
        _example(
            "omit-pass", JudgeType.OMITTED_EVIDENCE, HumanLabel.PASS,
            "The certificate carries grades, a school address, and a completion statement; only completion is "
            "extracted.",
            "Grades and the address do not bear on academic access, so leaving them out is not an omission.",
        ),
        _example(
            "omit-fail", JudgeType.OMITTED_EVIDENCE, HumanLabel.FAIL,
            "The Bemerkungen line legibly restricts the qualification to one Land and no restriction is recorded.",
            "A territorial restriction bears directly on academic access and is legible, so it should have been "
            "extracted.",
        ),
        _example(
            "omit-borderline", JudgeType.OMITTED_EVIDENCE, HumanLabel.FAIL,
            "A second certificate states a completion date contradicting the first, and only the first is recorded.",
            "The contradicting document is legible and bears on access. Whether it changes the status is for the "
            "rules engine; the omission itself is the failure.",
            borderline=True,
        ),
    ),
    JudgeType.EVIDENCE_STATE: (
        _example(
            "state-pass", JudgeType.EVIDENCE_STATE, HumanLabel.PASS,
            "A scan has an ink blot over the Land name. validity_restriction_present is KNOWN true and "
            "validity_restriction_code is UNREADABLE.",
            "The presence of a restriction is legible and its scope is not, so the two facts correctly carry "
            "different states.",
        ),
        _example(
            "state-fail", JudgeType.EVIDENCE_STATE, HumanLabel.FAIL,
            "The same blotted scan records validity_restriction_code as KNOWN with a Land taken from the school "
            "address.",
            "The field is present and unreadable, so the state must be UNREADABLE. KNOWN over an illegible field is "
            "a guess presented as a reading.",
        ),
        _example(
            "state-borderline", JudgeType.EVIDENCE_STATE, HumanLabel.FAIL,
            "Two certificates give different completion dates and the later one is recorded as KNOWN.",
            "Both are legible and they cannot both hold, so the state is CONFLICTING. Picking one hides the "
            "disagreement from the evaluator.",
            borderline=True,
        ),
    ),
}


def main() -> int:
    """Run one judge over one screened application and print the verdict."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="directory holding the two artifacts")
    parser.add_argument("--pdf", type=Path, action="append", required=True, help="applicant PDF, repeatable")
    parser.add_argument("--judge", default=JudgeType.EVIDENCE_STATE, type=JudgeType)
    parser.add_argument("--model", default=None, help="defaults to ADMISSIONS_OPENAI_MODEL")
    args = parser.parse_args()

    settings = AdmissionsSettings()
    if settings.openai_api_key is None:
        raise SystemExit("Set OPENAI_API_KEY in .env or the environment.")

    artifact = ApplicationFactsArtifact.model_validate_json((args.run_dir / "application-facts.json").read_text())
    result = ApplicationResult.model_validate_json((args.run_dir / "application-result.json").read_text())

    request = JudgeRequest(
        fixture_id=args.run_dir.name,
        judge=args.judge,
        pdf_paths=tuple(args.pdf),
        facts=artifact.facts,
        result=result,
        instructions=build_judge_instructions(args.judge, EXAMPLES[args.judge]),
        model=args.model or settings.openai_model,
        prompt_version="demo/1.0",
        max_output_tokens=4_000,
    )

    outcome = OpenAIJudgeAdapter(build_judge_client(settings)).evaluate(request)
    saved = save_verdict(args.run_dir, args.run_dir.name, args.judge, request.model, outcome)
    if isinstance(outcome, JudgeSucceeded):
        print(f"judge     {args.judge}")
        print(f"result    {outcome.verdict.result}")
        print(f"critique  {outcome.verdict.critique}")
        print(f"claims    {list(outcome.verdict.affected_claims)}")
        print(f"pages     {[(p.document_number, p.page_number) for p in outcome.verdict.affected_pages]}")
        print(f"cost      {outcome.usage.input_tokens} in, {outcome.usage.output_tokens} out, {outcome.duration_ms} ms")
        print(f"saved     {saved}")
        print("\nNot calibrated. The few-shot examples stand in for expert labels.")
        return 0

    print(f"judge failed: {outcome.category} {outcome.code} retryable={outcome.retryable}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
