from types import SimpleNamespace
from typing import Any, cast

import httpx
from openai import APITimeoutError, OpenAI

from app.adapters.openai_model import OpenAIAdmissionsModelAdapter
from app.models.facts import ApplicationFacts
from app.models.programs import ProgramContext
from app.services.ports import (
    ExtractApplicationFactsRequest,
    PdfModelInput,
    ProviderFailed,
    ProviderIncomplete,
    ProviderRefused,
    ProviderSucceeded,
)


def _facts() -> ApplicationFacts:
    return ApplicationFacts(
        schema_version="2.0",
        school_qualifications=(),
        advanced_vocational_qualifications=(),
        professional_access_candidates=(),
    )


def _program() -> ProgramContext:
    return ProgramContext.model_validate(
        {
            "catalog_version": "0.1",
            "program_id": "BACHELOR",
            "display_name": "Bachelor's Study Program",
            "study_level": "BACHELOR",
            "program_subject": "COMPUTER_SCIENCE",
            "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
        }
    )


def _request() -> ExtractApplicationFactsRequest:
    return ExtractApplicationFactsRequest(
        documents=(
            PdfModelInput(
                document_id="sha256:" + "a" * 64,
                filename="school.pdf",
                content=b"%PDF-1.7 school",
            ),
            PdfModelInput(
                document_id="sha256:" + "b" * 64,
                filename="work.pdf",
                content=b"%PDF-1.7 work",
            ),
        ),
        program=_program(),
        model="gpt-5.4-mini",
        prompt_version="application-facts/2.0",
        max_output_tokens=8_000,
    )


class _Usage:
    input_tokens = 100
    output_tokens = 40


class _CompletedResponse:
    status = "completed"
    output: list[object] = []
    output_parsed = _facts()
    model = "gpt-5.4-mini"
    usage = _Usage()
    _request_id = "req_fixture"


class _FakeResponses:
    def __init__(self, response: object | None = None) -> None:
        self.response = response or _CompletedResponse()
        self.kwargs: dict[str, Any] | None = None

    def parse(self, **kwargs: Any) -> object:
        self.kwargs = kwargs
        return self.response


class _FakeClient:
    def __init__(self, responses: object | None = None) -> None:
        self.responses = responses or _FakeResponses()


def test_openai_extraction_uses_one_direct_pdf_structured_output_call() -> None:
    """The complete bundle produces final ApplicationFacts with no draft call."""
    client = _FakeClient()
    adapter = OpenAIAdmissionsModelAdapter(cast(OpenAI, client))

    result = adapter.extract_application_facts(_request())

    assert isinstance(result, ProviderSucceeded)
    assert result.output is _CompletedResponse.output_parsed
    assert result.request_id == "req_fixture"
    responses = cast(_FakeResponses, client.responses)
    assert responses.kwargs is not None
    assert responses.kwargs["store"] is False
    assert responses.kwargs["text_format"] is ApplicationFacts
    content = responses.kwargs["input"][0]["content"]
    assert sum(item["type"] == "input_file" for item in content) == 2
    assert any("BACHELOR" in item.get("text", "") for item in content)
    assert any("sha256:" + "a" * 64 in item.get("text", "") for item in content)


def test_openai_extraction_translates_refusal_without_facts() -> None:
    """A refusal cannot become missing facts or reach deterministic evaluation."""
    response = SimpleNamespace(
        status="completed",
        output=[SimpleNamespace(type="message", content=[SimpleNamespace(type="refusal")])],
        output_parsed=None,
        model="gpt-5.4-mini",
        usage=_Usage(),
        _request_id="req_refused",
    )

    result = OpenAIAdmissionsModelAdapter(
        cast(OpenAI, _FakeClient(_FakeResponses(response)))
    ).extract_application_facts(_request())

    assert isinstance(result, ProviderRefused)
    assert result.request_id == "req_refused"


def test_openai_extraction_translates_incomplete_without_partial_facts() -> None:
    """Output-token exhaustion remains a typed incomplete provider result."""
    response = SimpleNamespace(
        status="incomplete",
        incomplete_details=SimpleNamespace(reason="max_output_tokens"),
        output=[],
        output_parsed=None,
        model="gpt-5.4-mini",
        usage=_Usage(),
        _request_id="req_incomplete",
    )

    result = OpenAIAdmissionsModelAdapter(
        cast(OpenAI, _FakeClient(_FakeResponses(response)))
    ).extract_application_facts(_request())

    assert isinstance(result, ProviderIncomplete)
    assert result.reason == "MAX_OUTPUT_TOKENS"


def test_openai_extraction_rejects_completed_response_without_parsed_facts() -> None:
    """A completed but malformed response is not normalized into empty facts."""
    response = SimpleNamespace(
        status="completed",
        output=[],
        output_parsed=None,
        model="gpt-5.4-mini",
        usage=_Usage(),
        _request_id="req_invalid",
    )

    result = OpenAIAdmissionsModelAdapter(
        cast(OpenAI, _FakeClient(_FakeResponses(response)))
    ).extract_application_facts(_request())

    assert isinstance(result, ProviderFailed)
    assert result.category == "INVALID_OUTPUT"


class _TimingOutResponses:
    def parse(self, **_: Any) -> object:
        raise APITimeoutError(httpx.Request("POST", "https://api.openai.com/v1/responses"))


def test_openai_extraction_translates_timeout_without_facts() -> None:
    """Transient provider failure is safe and contains no applicant content."""
    result = OpenAIAdmissionsModelAdapter(
        cast(OpenAI, _FakeClient(_TimingOutResponses()))
    ).extract_application_facts(_request())

    assert isinstance(result, ProviderFailed)
    assert result.category == "TIMEOUT"
    assert result.code == "OPENAI_TIMEOUT"
