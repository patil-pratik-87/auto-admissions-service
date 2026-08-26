"""OpenAI Responses adapter for evaluation-only semantic judges."""

import base64
from pathlib import Path
from time import perf_counter

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)
from openai.types.responses import ResponseInputContentParam, ResponseInputItemParam

from evals.judges.judges import (
    JudgeFailed,
    JudgeFailureCategory,
    JudgeModelPort,
    JudgeProviderResult,
    JudgeRequest,
    JudgeSucceeded,
    JudgeUsage,
    JudgeVerdict,
)


class OpenAIJudgeAdapter(JudgeModelPort):
    """Run one strict OpenAI Responses call for an approved synthetic case."""

    def __init__(self, client: OpenAI) -> None:
        """Initialize with a client configured for zero automatic retries."""
        self._client = client

    def evaluate(self, request: JudgeRequest) -> JudgeProviderResult:
        """Evaluate one semantic criterion without producing an applicant result."""
        started = perf_counter()
        try:
            content = self._build_content(request.pdf_paths, request)
        except OSError:
            return self._failure(
                started,
                JudgeFailureCategory.PROVIDER,
                "JUDGE_PDF_READ_FAILED",
                retryable=False,
            )

        input_items: list[ResponseInputItemParam] = [{"role": "user", "content": content}]
        try:
            response = self._client.responses.parse(
                model=request.model,
                instructions=request.instructions,
                input=input_items,
                text_format=JudgeVerdict,
                max_output_tokens=request.max_output_tokens,
                store=False,
            )
        except (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError):
            return self._failure(
                started,
                JudgeFailureCategory.PROVIDER,
                "JUDGE_PROVIDER_TRANSIENT",
                retryable=True,
            )
        except (AuthenticationError, PermissionDeniedError, BadRequestError, NotFoundError):
            return self._failure(
                started,
                JudgeFailureCategory.PROVIDER,
                "JUDGE_PROVIDER_CONFIGURATION",
                retryable=False,
            )
        except APIError:
            return self._failure(
                started,
                JudgeFailureCategory.PROVIDER,
                "JUDGE_PROVIDER_FAILED",
                retryable=False,
            )

        if response.status == "incomplete":
            reason = (response.incomplete_details.reason if response.incomplete_details else None) or "unknown"
            return self._failure(
                started,
                JudgeFailureCategory.INCOMPLETE,
                f"JUDGE_INCOMPLETE_{reason.upper()}",
                retryable=reason == "max_output_tokens",
            )
        if response.status != "completed":
            return self._failure(
                started,
                JudgeFailureCategory.PROVIDER,
                "JUDGE_RESPONSE_NOT_COMPLETED",
                retryable=False,
            )

        for output in response.output:
            if output.type != "message":
                continue
            if any(item.type == "refusal" for item in output.content):
                return self._failure(
                    started,
                    JudgeFailureCategory.REFUSAL,
                    "JUDGE_REFUSED",
                    retryable=False,
                )

        verdict = response.output_parsed
        if verdict is None:
            return self._failure(
                started,
                JudgeFailureCategory.INVALID_OUTPUT,
                "JUDGE_INVALID_OUTPUT",
                retryable=False,
            )

        usage = response.usage
        return JudgeSucceeded(
            kind="SUCCEEDED",
            verdict=verdict,
            model_returned=response.model,
            usage=JudgeUsage(
                input_tokens=usage.input_tokens if usage is not None else 0,
                output_tokens=usage.output_tokens if usage is not None else 0,
            ),
            duration_ms=self._duration_ms(started),
        )

    @staticmethod
    def _build_content(pdf_paths: tuple[Path, ...], request: JudgeRequest) -> list[ResponseInputContentParam]:
        content: list[ResponseInputContentParam] = [
            {
                "type": "input_text",
                "text": (
                    f"Synthetic fixture ID: {request.fixture_id}\n\n"
                    "Structured application facts used by the evaluator:\n"
                    f"{request.facts.model_dump_json()}\n\n"
                    "Deterministic academic-access result:\n"
                    f"{request.result.model_dump_json()}"
                ),
            }
        ]
        for pdf_path in pdf_paths:
            encoded = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
            content.append(
                {
                    "type": "input_file",
                    "filename": pdf_path.name,
                    "file_data": f"data:application/pdf;base64,{encoded}",
                }
            )
        return content

    @classmethod
    def _failure(
        cls,
        started: float,
        category: JudgeFailureCategory,
        code: str,
        *,
        retryable: bool,
    ) -> JudgeFailed:
        return JudgeFailed(
            kind="FAILED",
            category=category,
            code=code,
            retryable=retryable,
            duration_ms=cls._duration_ms(started),
        )

    @staticmethod
    def _duration_ms(started: float) -> int:
        return max(0, round((perf_counter() - started) * 1000))
