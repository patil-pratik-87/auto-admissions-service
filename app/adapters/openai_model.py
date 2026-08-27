"""OpenAI Responses adapter for runtime extraction and optional paraphrasing."""

import base64
from pathlib import Path
from time import perf_counter
from typing import Any, cast

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

from app.models.facts import ApplicationFacts
from app.services.ports import (
    ExtractApplicationFactsRequest,
    ExtractionProviderResult,
    IncompleteReason,
    ParaphraseDraft,
    ParaphraseProviderResult,
    ParaphraseRequest,
    ProviderErrorCategory,
    ProviderFailed,
    ProviderIncomplete,
    ProviderRefused,
    ProviderSucceeded,
    ProviderUsage,
)

EXTRACTION_PROMPT_VERSION = "application-facts/2.0"
PARAPHRASE_PROMPT_VERSION = "application-result-paraphrase/2.0"

_PROMPTS_ROOT = Path(__file__).resolve().parents[2] / "prompts"


def _load_prompt(prompt_version: str) -> str:
    """Read one versioned prompt file, failing at import if it is absent."""
    return (_PROMPTS_ROOT / f"{prompt_version}.md").read_text(encoding="utf-8")


_EXTRACTION_INSTRUCTIONS = _load_prompt(EXTRACTION_PROMPT_VERSION)
_PARAPHRASE_INSTRUCTIONS = _load_prompt(PARAPHRASE_PROMPT_VERSION)


class OpenAIAdmissionsModelAdapter:
    """Translate OpenAI Responses calls into the narrow runtime model port."""

    def __init__(self, client: OpenAI) -> None:
        """Initialize with an SDK client configured for zero automatic retries."""
        self._client = client

    def extract_application_facts(
        self,
        request: ExtractApplicationFactsRequest,
    ) -> ExtractionProviderResult:
        """Make one complete-bundle strict structured extraction attempt."""
        started = perf_counter()
        if request.prompt_version != EXTRACTION_PROMPT_VERSION:
            return self._failed(
                started,
                ProviderErrorCategory.INVALID_REQUEST,
                "UNSUPPORTED_EXTRACTION_PROMPT",
            )

        input_items: list[ResponseInputItemParam] = [
            {"role": "user", "content": self._extraction_content(request)}
        ]
        try:
            response = self._client.responses.parse(
                model=request.model,
                instructions=_EXTRACTION_INSTRUCTIONS,
                input=input_items,
                text_format=ApplicationFacts,
                max_output_tokens=request.max_output_tokens,
                store=False,
            )
        except APITimeoutError:
            return self._failed(started, ProviderErrorCategory.TIMEOUT, "OPENAI_TIMEOUT")
        except APIConnectionError:
            return self._failed(started, ProviderErrorCategory.CONNECTION, "OPENAI_CONNECTION")
        except RateLimitError:
            return self._failed(started, ProviderErrorCategory.RATE_LIMIT, "OPENAI_RATE_LIMIT")
        except InternalServerError:
            return self._failed(started, ProviderErrorCategory.SERVER, "OPENAI_SERVER")
        except AuthenticationError:
            return self._failed(started, ProviderErrorCategory.AUTHENTICATION, "OPENAI_AUTHENTICATION")
        except PermissionDeniedError:
            return self._failed(started, ProviderErrorCategory.PERMISSION, "OPENAI_PERMISSION")
        except NotFoundError:
            return self._failed(started, ProviderErrorCategory.MODEL_UNAVAILABLE, "OPENAI_MODEL_UNAVAILABLE")
        except BadRequestError:
            return self._failed(started, ProviderErrorCategory.INVALID_REQUEST, "OPENAI_INVALID_REQUEST")
        except APIError:
            return self._failed(started, ProviderErrorCategory.UNKNOWN, "OPENAI_PROVIDER_FAILED")

        request_id = self._request_id(response)
        if response.status == "incomplete":
            reason = (response.incomplete_details.reason if response.incomplete_details else None) or "unknown"
            return ProviderIncomplete(
                kind="INCOMPLETE",
                reason=(
                    IncompleteReason.MAX_OUTPUT_TOKENS
                    if reason == "max_output_tokens"
                    else IncompleteReason.OTHER
                ),
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )
        if response.status != "completed":
            return self._failed(
                started,
                ProviderErrorCategory.UNKNOWN,
                "OPENAI_RESPONSE_NOT_COMPLETED",
                request_id=request_id,
            )
        if self._contains_refusal(response.output):
            return ProviderRefused(
                kind="REFUSED",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )

        facts = response.output_parsed
        if not isinstance(facts, ApplicationFacts):
            return self._failed(
                started,
                ProviderErrorCategory.INVALID_OUTPUT,
                "OPENAI_INVALID_STRUCTURED_OUTPUT",
                request_id=request_id,
            )

        usage = response.usage
        return ProviderSucceeded[ApplicationFacts](
            kind="SUCCEEDED",
            output=facts,
            model_returned=response.model,
            request_id=request_id,
            usage=ProviderUsage(
                input_tokens=usage.input_tokens if usage is not None else 0,
                output_tokens=usage.output_tokens if usage is not None else 0,
            ),
            duration_ms=self._duration_ms(started),
        )

    def paraphrase_summary(self, request: ParaphraseRequest) -> ParaphraseProviderResult:
        """Make one optional presentation-only structured paraphrase attempt."""
        started = perf_counter()
        if request.prompt_version != PARAPHRASE_PROMPT_VERSION:
            return self._failed(
                started,
                ProviderErrorCategory.INVALID_REQUEST,
                "UNSUPPORTED_PARAPHRASE_PROMPT",
            )

        content: list[ResponseInputContentParam] = [
            {
                "type": "input_text",
                "text": (
                    "Authoritative deterministic result:\n"
                    f"{request.result.model_dump_json()}\n\n"
                    "Canonical summary:\n"
                    f"{request.canonical_summary.model_dump_json()}"
                ),
            }
        ]
        input_items: list[ResponseInputItemParam] = [{"role": "user", "content": content}]
        try:
            response = self._client.responses.parse(
                model=request.model,
                instructions=_PARAPHRASE_INSTRUCTIONS,
                input=input_items,
                text_format=ParaphraseDraft,
                max_output_tokens=request.max_output_tokens,
                store=False,
            )
        except APITimeoutError:
            return self._failed(started, ProviderErrorCategory.TIMEOUT, "OPENAI_TIMEOUT")
        except APIConnectionError:
            return self._failed(started, ProviderErrorCategory.CONNECTION, "OPENAI_CONNECTION")
        except RateLimitError:
            return self._failed(started, ProviderErrorCategory.RATE_LIMIT, "OPENAI_RATE_LIMIT")
        except InternalServerError:
            return self._failed(started, ProviderErrorCategory.SERVER, "OPENAI_SERVER")
        except AuthenticationError:
            return self._failed(started, ProviderErrorCategory.AUTHENTICATION, "OPENAI_AUTHENTICATION")
        except PermissionDeniedError:
            return self._failed(started, ProviderErrorCategory.PERMISSION, "OPENAI_PERMISSION")
        except NotFoundError:
            return self._failed(started, ProviderErrorCategory.MODEL_UNAVAILABLE, "OPENAI_MODEL_UNAVAILABLE")
        except BadRequestError:
            return self._failed(started, ProviderErrorCategory.INVALID_REQUEST, "OPENAI_INVALID_REQUEST")
        except APIError:
            return self._failed(started, ProviderErrorCategory.UNKNOWN, "OPENAI_PROVIDER_FAILED")

        request_id = self._request_id(response)
        if response.status == "incomplete":
            reason = (response.incomplete_details.reason if response.incomplete_details else None) or "unknown"
            return ProviderIncomplete(
                kind="INCOMPLETE",
                reason=(
                    IncompleteReason.MAX_OUTPUT_TOKENS
                    if reason == "max_output_tokens"
                    else IncompleteReason.OTHER
                ),
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )
        if response.status != "completed":
            return self._failed(
                started,
                ProviderErrorCategory.UNKNOWN,
                "OPENAI_RESPONSE_NOT_COMPLETED",
                request_id=request_id,
            )
        if self._contains_refusal(response.output):
            return ProviderRefused(
                kind="REFUSED",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )

        paraphrase = response.output_parsed
        if not isinstance(paraphrase, ParaphraseDraft):
            return self._failed(
                started,
                ProviderErrorCategory.INVALID_OUTPUT,
                "OPENAI_INVALID_STRUCTURED_OUTPUT",
                request_id=request_id,
            )
        usage = response.usage
        return ProviderSucceeded[ParaphraseDraft](
            kind="SUCCEEDED",
            output=paraphrase,
            model_returned=response.model,
            request_id=request_id,
            usage=ProviderUsage(
                input_tokens=usage.input_tokens if usage is not None else 0,
                output_tokens=usage.output_tokens if usage is not None else 0,
            ),
            duration_ms=self._duration_ms(started),
        )

    @staticmethod
    def _extraction_content(request: ExtractApplicationFactsRequest) -> list[ResponseInputContentParam]:
        bundle_map = "\n".join(
            f"- document_id={document.document_id!r} filename={document.filename!r} pages={document.page_count}"
            for document in request.documents
        )
        content: list[ResponseInputContentParam] = [
            {
                "type": "input_text",
                "text": (
                    "Trusted selected program context:\n"
                    f"{request.program.model_dump_json()}\n\n"
                    "Trusted document ID map:\n"
                    f"{bundle_map}"
                ),
            }
        ]
        for document in request.documents:
            encoded = base64.b64encode(document.content).decode("ascii")
            content.append(
                {
                    "type": "input_file",
                    "filename": document.filename,
                    "file_data": f"data:application/pdf;base64,{encoded}",
                }
            )
        return content

    @staticmethod
    def _contains_refusal(output: list[Any]) -> bool:
        for item in output:
            if getattr(item, "type", None) != "message":
                continue
            if any(getattr(content, "type", None) == "refusal" for content in item.content):
                return True
        return False

    @classmethod
    def _failed(
        cls,
        started: float,
        category: ProviderErrorCategory,
        code: str,
        *,
        request_id: str | None = None,
    ) -> ProviderFailed:
        return ProviderFailed(
            kind="FAILED",
            category=category,
            code=code,
            duration_ms=cls._duration_ms(started),
            request_id=request_id,
        )

    @staticmethod
    def _request_id(response: object) -> str | None:
        return cast(str | None, getattr(response, "_request_id", None))

    @staticmethod
    def _duration_ms(started: float) -> int:
        return max(0, round((perf_counter() - started) * 1000))
