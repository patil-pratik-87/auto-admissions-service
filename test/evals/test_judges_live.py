"""Run the three judges over real synthetic bundles, against the live OpenAI API.

Opt in with `uv run pytest -m live_openai`. This spends tokens and calls OpenAI, so it is
deselected from the default suite.

Every persona here is one the extractor is expected to read correctly, so every judge should
return PASS. A FAIL is a real signal, meaning either extraction regressed or the judge is
miscalibrated, and the critique names which.
"""

import json
import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.bootstrap import AdmissionsSettings, build_screening
from app.interface import RunFailed, ScreenCompleted, ScreenRequest
from evals.judges.judge_prompts import build_judge_instructions
from evals.judges.judge_validation import HumanLabel, JudgeType
from evals.judges.judges import JudgeRequest, JudgeSucceeded
from evals.judges.openai_judge import OpenAIJudgeAdapter
from evals.judges.report import build_report
from evals.judges.run_judge import EXAMPLES, build_judge_client, save_verdict

MODEL = os.getenv("JUDGE_EVAL_MODEL", "gpt-5.4-mini")
SAMPLES = Path("samples/filled-documents")
OUTPUT_ROOT = Path("runs/judges-live")

# One persona per way extraction is asked to behave, taken from the evaluation tuples.
PERSONAS = (
    ("felix-brandt", "ELIGIBLE", "clean Abitur, nothing to infer"),
    ("sarah-koenig", "MISSING_INFORMATION", "blotted scan, the Land must stay UNREADABLE"),
    ("anna-beispiel", "ELIGIBLE", "two documents combine into one qualification"),
    ("jonas-krause", "MISSING_INFORMATION", "vocational part absent, must not be guessed"),
    ("daniel-roth", "MISSING_INFORMATION", "employment duration derived from two dates"),
)


def _bundle(persona: str) -> tuple[Path, ...]:
    """The digital PDFs for one persona, or the scan where only a scan exists."""
    folder = SAMPLES / persona
    digital = sorted(p for p in folder.glob("*.pdf") if not p.name.endswith("-scan.pdf"))
    return tuple(digital or sorted(folder.glob("*.pdf")))


@pytest.fixture(scope="module")
def settings() -> AdmissionsSettings:
    """Settings shared by screening and judging, with the model pinned."""
    loaded = AdmissionsSettings()
    if loaded.openai_api_key is None:
        pytest.skip("OPENAI_API_KEY is not set")
    return loaded


@pytest.fixture(scope="module")
def judge_adapter(settings: AdmissionsSettings) -> OpenAIJudgeAdapter:
    """One judge adapter for the whole module, traced to the judge LangSmith project."""
    return OpenAIJudgeAdapter(build_judge_client(settings))


@pytest.fixture(scope="module")
def screened(settings: AdmissionsSettings) -> Iterator[dict[str, ScreenCompleted | RunFailed]]:
    """Screen each persona once, not once per judge. A failure is reported by its own test."""
    workflow = build_screening(settings)
    runs: dict[str, ScreenCompleted | RunFailed] = {}
    for persona, expected, _ in PERSONAS:
        outcome = workflow.screen(
            ScreenRequest(
                program_id="BACHELOR",
                pdf_paths=_bundle(persona),
                output_dir=OUTPUT_ROOT / persona,
                model=MODEL,
                overwrite=True,
            )
        )
        runs[persona] = outcome
        actual = outcome.result.application_status if isinstance(outcome, ScreenCompleted) else "screen failed"
        folder = OUTPUT_ROOT / persona
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "screening.json").write_text(
            json.dumps({"persona": persona, "expected": expected, "actual": str(actual), "model": MODEL}, indent=2)
        )
    yield runs
    print(f"\njudge run report: {build_report(OUTPUT_ROOT)}")


@pytest.mark.live_openai
@pytest.mark.parametrize(("persona", "expected_status", "angle"), PERSONAS, ids=[p[0] for p in PERSONAS])
@pytest.mark.parametrize("judge", tuple(JudgeType), ids=lambda j: str(j))
def test_judges_pass_on_correctly_extracted_bundles(
    persona: str,
    expected_status: str,
    angle: str,
    judge: JudgeType,
    screened: dict[str, ScreenCompleted | RunFailed],
    judge_adapter: OpenAIJudgeAdapter,
) -> None:
    """Screen one real bundle, then ask one judge whether the extraction holds up."""
    run = screened[persona]
    assert isinstance(run, ScreenCompleted), f"{persona} ({angle}) failed to screen on {MODEL}: {run}"
    assert run.result.application_status == expected_status, (
        f"{persona} ({angle}) gave {run.result.application_status}, expected {expected_status}"
    )

    outcome = judge_adapter.evaluate(
        JudgeRequest(
            fixture_id=persona,
            judge=judge,
            pdf_paths=_bundle(persona),
            facts=run.artifact.facts,
            result=run.result,
            instructions=build_judge_instructions(judge, EXAMPLES[judge]),
            model=MODEL,
            prompt_version="demo/1.0",
            max_output_tokens=4_000,
        )
    )
    save_verdict(OUTPUT_ROOT / persona, persona, judge, MODEL, outcome)
    assert isinstance(outcome, JudgeSucceeded), f"{judge} errored on {persona}: {outcome}"
    assert outcome.verdict.result is HumanLabel.PASS, (
        f"{judge} failed {persona} ({angle}): {outcome.verdict.critique}"
    )
