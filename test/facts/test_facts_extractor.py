from collections.abc import Sequence
from hashlib import sha256
from pathlib import Path

import pytest

from app.facts import FactsExtractor
from app.facts.config import FactsSettings
from app.models.facts import ApplicationFacts
from app.models.programs import PolicyRef, ProgramContext
from app.services.ports import (
    ExtractApplicationFactsRequest,
    ExtractionProviderResult,
    IncompleteReason,
    ParaphraseProviderResult,
    ParaphraseRequest,
    ProviderErrorCategory,
    ProviderFailed,
    ProviderIncomplete,
    ProviderRefused,
    ProviderSucceeded,
    ProviderUsage,
)


class ScriptedModel:
    """Return caller-supplied one-attempt extraction results without network access."""

    def __init__(self, results: Sequence[ExtractionProviderResult]) -> None:
        self._results = list(results)
        self.requests: list[ExtractApplicationFactsRequest] = []

    def extract_application_facts(self, request: ExtractApplicationFactsRequest) -> ExtractionProviderResult:
        self.requests.append(request)
        if not self._results:
            raise AssertionError("The facts extractor exceeded the scripted attempt count")
        return self._results.pop(0)

    def paraphrase_summary(self, request: ParaphraseRequest) -> ParaphraseProviderResult:
        raise AssertionError("The facts extractor cannot paraphrase decisions")


class ScriptedPreflight:
    """Accept any well-formed PDF header and script its page count."""

    def __init__(self, page_count: int = 1) -> None:
        self.page_count = page_count

    def accept(self, content: bytes) -> int:
        assert content.startswith(b"%PDF-")
        return self.page_count


def _program() -> ProgramContext:
    return ProgramContext(
        catalog_version="0.1",
        program_id="BACHELOR",
        display_name="Bachelor's Study Program",
        study_level="BACHELOR",
        program_subject="COMPUTER_SCIENCE",
        policy=PolicyRef(id="IU_BACHELOR_ACCESS", version="0.0.22"),
    )


def _empty_facts() -> ApplicationFacts:
    return ApplicationFacts(
        schema_version="2.0",
        school_qualifications=(),
        advanced_vocational_qualifications=(),
        professional_access_candidates=(),
    )


def _success(facts: ApplicationFacts | None = None, *, model: str = "gpt-returned") -> ExtractionProviderResult:
    return ProviderSucceeded[ApplicationFacts](
        kind="SUCCEEDED",
        output=facts or _empty_facts(),
        model_returned=model,
        request_id="request-safe",
        usage=ProviderUsage(input_tokens=10, output_tokens=20),
        duration_ms=3,
    )


def _write_stub_pdf(path: Path) -> Path:
    path.write_bytes(b"%PDF-1.7\nscripted fixture")
    return path


def _facts_with_evidence(document_id: str, page_number: int) -> ApplicationFacts:
    def missing(fact_id: str) -> dict[str, object]:
        return {"state": "MISSING", "fact_id": fact_id, "evidence": []}

    return ApplicationFacts.model_validate(
        {
            "schema_version": "2.0",
            "school_qualifications": [
                {
                    "qualification_id": "school-001",
                    "type": {
                        "state": "KNOWN",
                        "fact_id": "school-001.type",
                        "value": "ALLGEMEINE_HOCHSCHULREIFE",
                        "evidence": [
                            {
                                "document_id": document_id,
                                "page_number": page_number,
                                "excerpt": "Allgemeine Hochschulreife",
                            }
                        ],
                    },
                    "country": missing("school-001.country"),
                    "completed": missing("school-001.completed"),
                    "access_scope": missing("school-001.access_scope"),
                    "validity_restriction_present": missing("school-001.validity_restriction_present"),
                    "validity_restriction_code": missing("school-001.validity_restriction_code"),
                    "school_part_proven": missing("school-001.school_part_proven"),
                    "vocational_part_proven": missing("school-001.vocational_part_proven"),
                    "issuing_region": missing("school-001.issuing_region"),
                }
            ],
            "advanced_vocational_qualifications": [],
            "professional_access_candidates": [],
        }
    )


def test_build_deduplicates_exact_real_pdf_bytes_and_keeps_model_facts_unchanged(tmp_path: Path) -> None:
    """One complete canonical bundle is sent and strict model facts become artifact 2.0 unchanged."""
    source = Path("samples/filled-documents/sofia-lorenz/abitur-zeugnis.pdf")
    first = tmp_path / "a-certificate.pdf"
    duplicate = tmp_path / "z-copy.pdf"
    first.write_bytes(source.read_bytes())
    duplicate.write_bytes(source.read_bytes())
    facts = _empty_facts()
    model = ScriptedModel((_success(facts),))

    outcome = FactsExtractor(model=model).extract(
        run_id="run-direct",
        program=_program(),
        pdf_paths=(duplicate, first),
        model_override="gpt-requested",
    )

    assert outcome.kind == "EXTRACTION_SUCCEEDED"
    assert outcome.artifact.artifact_version == "2.0"
    assert outcome.artifact.facts is facts
    assert outcome.artifact.manifest.total_pages == 5
    assert len(outcome.artifact.manifest.documents) == 1
    assert outcome.artifact.manifest.documents[0].original_filename == "a-certificate.pdf"
    assert outcome.artifact.manifest.documents[0].duplicate_filenames == ("z-copy.pdf",)
    assert len(model.requests) == 1
    assert model.requests[0].documents[0].content == source.read_bytes()
    assert model.requests[0].program == _program()
    assert model.requests[0].model == "gpt-requested"
    assert outcome.artifact.versions.extraction_prompt == "application-facts/2.0"


def test_build_rejects_a_missing_pdf_before_provider_use(tmp_path: Path) -> None:
    """A missing input is a typed ingestion failure, never empty application facts."""
    model = ScriptedModel((_success(),))

    outcome = FactsExtractor(model=model).extract(
        run_id="run-missing",
        program=_program(),
        pdf_paths=(tmp_path / "missing.pdf",),
    )

    assert outcome.kind == "EXTRACTION_FAILED"
    assert outcome.failure.stage == "PDF_INGESTION"
    assert outcome.failure.code == "PATH_NOT_FOUND"
    assert outcome.failure.retryable is False
    assert model.requests == []


@pytest.mark.parametrize("reference_kind", ("UNKNOWN_DOCUMENT", "OUT_OF_RANGE_PAGE"))
def test_build_rejects_evidence_references_outside_the_manifest(
    tmp_path: Path,
    reference_kind: str,
) -> None:
    """Structural citation checks reject unknown documents and out-of-range pages without OCR."""
    pdf_path = _write_stub_pdf(tmp_path / "input.pdf")
    manifest_document_id = f"sha256:{sha256(pdf_path.read_bytes()).hexdigest()}"
    document_id = "sha256:" + "0" * 64 if reference_kind == "UNKNOWN_DOCUMENT" else manifest_document_id
    page_number = 2 if reference_kind == "OUT_OF_RANGE_PAGE" else 1
    model = ScriptedModel((_success(_facts_with_evidence(document_id, page_number)),))

    outcome = FactsExtractor(model=model, preflight=ScriptedPreflight()).extract(
        run_id="run-reference",
        program=_program(),
        pdf_paths=(pdf_path,),
    )

    assert outcome.kind == "EXTRACTION_FAILED"
    assert outcome.failure.stage == "FACTS_VALIDATION"
    assert outcome.failure.code == "INVALID_EVIDENCE_REFERENCE"
    assert outcome.failure.retryable is False


def test_build_retries_one_retryable_provider_failure_then_succeeds(tmp_path: Path) -> None:
    """The module, rather than the adapter, owns the two-total-attempt ceiling."""
    pdf_path = _write_stub_pdf(tmp_path / "input.pdf")
    model = ScriptedModel(
        (
            ProviderFailed(
                kind="FAILED",
                category=ProviderErrorCategory.CONNECTION,
                code="CONNECTION_FAILED",
                duration_ms=1,
            ),
            _success(),
        )
    )

    outcome = FactsExtractor(model=model, preflight=ScriptedPreflight()).extract(
        run_id="run-retry",
        program=_program(),
        pdf_paths=(pdf_path,),
    )

    assert outcome.kind == "EXTRACTION_SUCCEEDED"
    assert len(model.requests) == 2
    assert tuple(attempt.response_status for attempt in outcome.artifact.attempts) == ("FAILED", "SUCCEEDED")


def test_build_retries_output_token_exhaustion_once_with_a_larger_limit(tmp_path: Path) -> None:
    """Only output-token exhaustion changes the second request's output cap."""
    pdf_path = _write_stub_pdf(tmp_path / "input.pdf")
    model = ScriptedModel(
        (
            ProviderIncomplete(kind="INCOMPLETE", reason=IncompleteReason.MAX_OUTPUT_TOKENS, duration_ms=1),
            _success(),
        )
    )

    outcome = FactsExtractor(model=model, preflight=ScriptedPreflight()).extract(
        run_id="run-output-limit",
        program=_program(),
        pdf_paths=(pdf_path,),
    )

    assert outcome.kind == "EXTRACTION_SUCCEEDED"
    assert tuple(request.max_output_tokens for request in model.requests) == (8_000, 16_000)


@pytest.mark.parametrize(
    ("provider_result", "expected_code", "expected_retryable"),
    (
        (ProviderRefused(kind="REFUSED", duration_ms=1), "EXTRACTION_REFUSED", False),
        (
            ProviderIncomplete(kind="INCOMPLETE", reason=IncompleteReason.OTHER, duration_ms=1),
            "EXTRACTION_INCOMPLETE",
            False,
        ),
        (
            ProviderFailed(
                kind="FAILED",
                category=ProviderErrorCategory.INVALID_OUTPUT,
                code="INVALID_STRUCTURED_OUTPUT",
                duration_ms=1,
            ),
            "EXTRACTION_INVALID_OUTPUT",
            False,
        ),
    ),
)
def test_build_never_accepts_non_success_provider_results(
    tmp_path: Path,
    provider_result: ExtractionProviderResult,
    expected_code: str,
    expected_retryable: bool,
) -> None:
    """Refusal, incomplete, and malformed output remain processing failures."""
    pdf_path = _write_stub_pdf(tmp_path / "input.pdf")
    model = ScriptedModel((provider_result,))

    outcome = FactsExtractor(model=model, preflight=ScriptedPreflight()).extract(
        run_id="run-provider-failure",
        program=_program(),
        pdf_paths=(pdf_path,),
    )

    assert outcome.kind == "EXTRACTION_FAILED"
    assert outcome.failure.stage == "EXTRACTION"
    assert outcome.failure.code == expected_code
    assert outcome.failure.retryable is expected_retryable
    assert len(model.requests) == 1


def test_build_enforces_the_configured_page_limit_before_provider_use() -> None:
    """A valid but oversized real PDF fails all-or-nothing preflight."""
    model = ScriptedModel((_success(),))
    settings = FactsSettings(max_total_pages=4)

    outcome = FactsExtractor(model=model, settings=settings).extract(
        run_id="run-pages",
        program=_program(),
        pdf_paths=(Path("samples/filled-documents/sofia-lorenz/abitur-zeugnis.pdf"),),
    )

    assert outcome.kind == "EXTRACTION_FAILED"
    assert outcome.failure.code == "BATCH_LIMIT_EXCEEDED"
    assert model.requests == []
