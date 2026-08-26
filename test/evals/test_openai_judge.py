from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import httpx
from openai import APITimeoutError, OpenAI

from app.models.facts import ApplicationFacts
from app.models.results import RULE_ORDER, ApplicationResult
from evals.judges.judge_validation import JudgeType
from evals.judges.judges import JudgeFailed, JudgeRequest, JudgeSucceeded, JudgeVerdict
from evals.judges.openai_judge import OpenAIJudgeAdapter


def _report() -> ApplicationResult:
    return ApplicationResult.model_validate(
        {
            "kind": "APPLICATION_RESULT",
            "result_version": "2.0",
            "run_id": "synthetic-run",
            "scope": "ACADEMIC_ACCESS_ONLY",
            "program": {"id": "BACHELOR", "display_name": "Bachelor's Study Program"},
            "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
            "application_status": "MANUAL_REVIEW",
            "application_reason_code": "NO_RECOGNIZED_ADMISSIONS_RULE",
            "rules": [
                {
                    "rule_id": rule_id,
                    "status": "NOT_APPLICABLE",
                    "reason_code": "NO_CANDIDATE_FOR_RULE",
                    "candidate_ids": [],
                    "fact_ids": [],
                    "evidence_ids": [],
                    "condition": None,
                }
                for rule_id in RULE_ORDER
            ],
            "missing_information": [],
            "manual_review": [],
            "warnings": [],
            "evidence": [],
            "summary": {
                "canonical": {
                    "headline": "Academic access requires manual review",
                    "explanation": "No submitted qualification matched a configured rule.",
                    "required_information": [],
                },
                "llm_paraphrase": None,
            },
        }
    )


class _Usage:
    input_tokens = 100
    output_tokens = 40


class _CompletedResponse:
    status = "completed"
    output: list[object] = []
    output_parsed = JudgeVerdict(
        critique="Every decision-relevant claim is supported by the supplied synthetic document.",
        affected_claims=(),
        affected_pages=(),
        result="PASS",
    )
    model = "judge-model-snapshot"
    usage = _Usage()


class _FakeResponses:
    def __init__(self) -> None:
        self.kwargs: dict[str, Any] | None = None

    def parse(self, **kwargs: Any) -> _CompletedResponse:
        self.kwargs = kwargs
        return _CompletedResponse()


class _FakeClient:
    def __init__(self) -> None:
        self.responses = _FakeResponses()


class _ClientWithResponses:
    def __init__(self, responses: object) -> None:
        self.responses = responses


def _request(pdf_path: Path) -> JudgeRequest:
    return JudgeRequest(
        fixture_id="synthetic-001",
        judge=JudgeType.FABRICATED_VALUE,
        pdf_paths=(pdf_path,),
        facts=ApplicationFacts(
            schema_version="2.0",
            school_qualifications=(),
            advanced_vocational_qualifications=(),
            professional_access_candidates=(),
        ),
        result=_report(),
        instructions="Assess document support only.",
        model="judge-model-snapshot",
        prompt_version="document-support/1.0",
        max_output_tokens=1200,
    )


def test_openai_judge_uses_direct_pdf_structured_output_without_response_storage(tmp_path: Path) -> None:
    """The live judge boundary sends approved PDFs and accepts only its strict verdict."""
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 synthetic fixture")
    fake_client = _FakeClient()
    adapter = OpenAIJudgeAdapter(cast(OpenAI, fake_client))
    request = _request(pdf_path)

    result = adapter.evaluate(request)

    assert isinstance(result, JudgeSucceeded)
    assert result.verdict.result == "PASS"
    assert fake_client.responses.kwargs is not None
    assert fake_client.responses.kwargs["store"] is False
    assert fake_client.responses.kwargs["text_format"] is JudgeVerdict
    content = fake_client.responses.kwargs["input"][0]["content"]
    input_text = next(item["text"] for item in content if item["type"] == "input_text")
    assert '"schema_version":"2.0"' in input_text
    assert any(
        item["type"] == "input_file" and item["file_data"].startswith("data:application/pdf;base64,")
        for item in content
    )


class _RefusingResponses:
    def parse(self, **_: Any) -> object:
        return SimpleNamespace(
            status="completed",
            output=[SimpleNamespace(type="message", content=[SimpleNamespace(type="refusal")])],
            output_parsed=None,
            model="judge-model-snapshot",
            usage=_Usage(),
        )


class _IncompleteResponses:
    def parse(self, **_: Any) -> object:
        return SimpleNamespace(
            status="incomplete",
            incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            output=[],
            output_parsed=None,
            model="judge-model-snapshot",
            usage=_Usage(),
        )


class _TimingOutResponses:
    def parse(self, **_: Any) -> object:
        raise APITimeoutError(httpx.Request("POST", "https://api.openai.com/v1/responses"))


def test_openai_judge_returns_evaluation_failure_for_refusal(tmp_path: Path) -> None:
    """A refusal is never converted into an uncertain or passing verdict."""
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 synthetic fixture")
    client = _ClientWithResponses(_RefusingResponses())

    result = OpenAIJudgeAdapter(cast(OpenAI, client)).evaluate(_request(pdf_path))

    assert isinstance(result, JudgeFailed)
    assert result.category == "REFUSAL"
    assert result.retryable is False


def test_openai_judge_marks_output_limit_incomplete_as_retryable_evaluation_failure(tmp_path: Path) -> None:
    """An incomplete response has no verdict and may be retried by the eval runner."""
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 synthetic fixture")
    client = _ClientWithResponses(_IncompleteResponses())

    result = OpenAIJudgeAdapter(cast(OpenAI, client)).evaluate(_request(pdf_path))

    assert isinstance(result, JudgeFailed)
    assert result.category == "INCOMPLETE"
    assert result.retryable is True


def test_openai_judge_translates_timeout_without_inventing_a_verdict(tmp_path: Path) -> None:
    """A provider outage stays an evaluation failure outside admissions runtime."""
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 synthetic fixture")
    client = _ClientWithResponses(_TimingOutResponses())

    result = OpenAIJudgeAdapter(cast(OpenAI, client)).evaluate(_request(pdf_path))

    assert isinstance(result, JudgeFailed)
    assert result.category == "PROVIDER"
    assert result.retryable is True
