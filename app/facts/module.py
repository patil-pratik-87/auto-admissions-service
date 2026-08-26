"""Deep direct-PDF-to-ApplicationFacts seam."""

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from pydantic import ValidationError

from app.facts.config import FactsSettings
from app.facts.documents import AcceptedDocument, PdfPreflight, PdfRejected
from app.io.documents import PyMuPDFPreflight
from app.models.artifacts import (
    ApplicationFactsArtifact,
    FactsArtifactVersions,
    ProviderAttemptMetadata,
)
from app.models.documents import DocumentManifest, DocumentManifestEntry
from app.models.facts import ApplicationFacts
from app.models.failures import FailureStage, ProcessingFailureReport
from app.models.outcomes import ExtractionFailed, ExtractionOutcome, ExtractionSucceeded
from app.models.programs import ProgramContext
from app.services.ports import (
    AdmissionsModelPort,
    ExtractApplicationFactsRequest,
    IncompleteReason,
    PdfModelInput,
    ProviderErrorCategory,
    ProviderFailed,
    ProviderIncomplete,
    ProviderRefused,
    ProviderSucceeded,
)

RETRYABLE_PROVIDER_CATEGORIES = frozenset(
    {
        ProviderErrorCategory.CONNECTION,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.SERVER,
    }
)


@dataclass(frozen=True, slots=True)
class _ModelExtraction:
    facts: ApplicationFacts
    model_returned: str
    attempts: tuple[ProviderAttemptMetadata, ...]


class FactsExtractor:
    """Preflight one PDF bundle and request strict final application facts."""

    def __init__(
        self,
        *,
        model: AdmissionsModelPort | None,
        preflight: PdfPreflight | None = None,
        settings: FactsSettings | None = None,
    ) -> None:
        """Initialize the extractor with its provider and local PDF preflight."""
        self._model = model
        self._preflight = preflight or PyMuPDFPreflight()
        self._settings = settings or FactsSettings()

    def extract(
        self,
        *,
        run_id: str,
        program: ProgramContext,
        pdf_paths: tuple[Path, ...],
        model_override: str | None = None,
    ) -> ExtractionOutcome:
        """Return one complete schema-2.0 artifact or a typed processing failure."""
        ingested = self._ingest(run_id, pdf_paths)
        if isinstance(ingested, ExtractionFailed):
            return ingested

        manifest, documents = ingested
        model_requested = model_override or self._settings.default_model
        extraction = self._extract(
            run_id=run_id,
            program=program,
            documents=documents,
            model_requested=model_requested,
        )
        if isinstance(extraction, ExtractionFailed):
            return extraction

        try:
            artifact = ApplicationFactsArtifact(
                kind="APPLICATION_FACTS",
                artifact_version="2.0",
                run_id=run_id,
                program=program,
                manifest=manifest,
                facts=extraction.facts,
                versions=FactsArtifactVersions(
                    extraction_prompt=self._settings.extraction_prompt_version,
                    model_requested=model_requested,
                    model_returned=extraction.model_returned,
                ),
                attempts=extraction.attempts,
            )
        except ValidationError:
            return _failure(
                run_id=run_id,
                stage=FailureStage.FACTS_VALIDATION,
                code="INVALID_EVIDENCE_REFERENCE",
                safe_message="The extracted facts contain a reference outside the supplied PDF bundle.",
                retryable=False,
            )
        return ExtractionSucceeded(kind="EXTRACTION_SUCCEEDED", artifact=artifact)

    def _extract(
        self,
        *,
        run_id: str,
        program: ProgramContext,
        documents: tuple[AcceptedDocument, ...],
        model_requested: str,
    ) -> _ModelExtraction | ExtractionFailed:
        attempts: list[ProviderAttemptMetadata] = []
        max_output_tokens = self._settings.initial_max_output_tokens
        if self._model is None:
            return self._extraction_failure(
                run_id,
                "OPENAI_API_KEY_MISSING",
                "The extraction provider is not configured.",
                retryable=False,
            )

        for attempt_number in (1, 2):
            request = ExtractApplicationFactsRequest(
                documents=tuple(
                    PdfModelInput(
                        document_id=document.manifest_entry.document_id,
                        filename=document.manifest_entry.original_filename,
                        content=document.content,
                    )
                    for document in documents
                ),
                program=program,
                model=model_requested,
                prompt_version=self._settings.extraction_prompt_version,
                max_output_tokens=max_output_tokens,
            )
            result = self._model.extract_application_facts(request)

            if isinstance(result, ProviderSucceeded):
                if not isinstance(result.output, ApplicationFacts):
                    return self._extraction_failure(
                        run_id,
                        "EXTRACTION_INVALID_OUTPUT",
                        "The extraction provider did not return valid structured application facts.",
                        retryable=False,
                    )
                attempts.append(
                    ProviderAttemptMetadata(
                        operation="EXTRACTION",
                        attempt_number=attempt_number,
                        model_requested=model_requested,
                        model_returned=result.model_returned,
                        response_status="SUCCEEDED",
                        request_id=result.request_id,
                        input_tokens=result.usage.input_tokens,
                        output_tokens=result.usage.output_tokens,
                        duration_ms=result.duration_ms,
                    )
                )
                return _ModelExtraction(
                    facts=result.output,
                    model_returned=result.model_returned,
                    attempts=tuple(attempts),
                )

            attempts.append(
                _attempt_metadata(
                    result,
                    attempt_number=attempt_number,
                    model_requested=model_requested,
                )
            )
            retryable = _provider_result_is_retryable(result)
            if retryable and attempt_number == 1:
                if isinstance(result, ProviderIncomplete) and result.reason is IncompleteReason.MAX_OUTPUT_TOKENS:
                    max_output_tokens = self._settings.retry_max_output_tokens
                continue
            return _provider_failure(run_id, result, retryable=retryable)

        return self._extraction_failure(
            run_id,
            "EXTRACTION_FAILED",
            "Application facts could not be extracted.",
            retryable=False,
        )

    def _ingest(
        self,
        run_id: str,
        pdf_paths: tuple[Path, ...],
    ) -> tuple[DocumentManifest, tuple[AcceptedDocument, ...]] | ExtractionFailed:
        if not pdf_paths:
            return self._ingestion_failure(run_id, "NO_INPUT", "At least one PDF is required.")

        contents_by_digest: dict[str, bytes] = {}
        paths_by_digest: dict[str, list[Path]] = defaultdict(list)
        for path in pdf_paths:
            try:
                if not path.exists():
                    return self._ingestion_failure(run_id, "PATH_NOT_FOUND", "An input PDF was not found.")
                if not path.is_file():
                    return self._ingestion_failure(run_id, "NOT_REGULAR_FILE", "An input path is not a regular file.")
                content = path.read_bytes()
            except OSError:
                return self._ingestion_failure(run_id, "PATH_NOT_READABLE", "An input PDF could not be read.")
            digest = sha256(content).hexdigest()
            contents_by_digest.setdefault(digest, content)
            paths_by_digest[digest].append(path)

        if len(contents_by_digest) > self._settings.max_unique_pdfs:
            return self._ingestion_failure(run_id, "BATCH_LIMIT_EXCEEDED", "The PDF bundle exceeds its file limit.")
        if sum(len(content) for content in contents_by_digest.values()) > self._settings.max_total_bytes:
            return self._ingestion_failure(run_id, "BATCH_LIMIT_EXCEEDED", "The PDF bundle exceeds its byte limit.")

        accepted: list[AcceptedDocument] = []
        total_pages = 0
        for digest in sorted(contents_by_digest):
            content = contents_by_digest[digest]
            if len(content) > self._settings.max_file_bytes:
                return self._ingestion_failure(run_id, "BATCH_LIMIT_EXCEEDED", "An input PDF exceeds its byte limit.")
            try:
                page_count = self._preflight.accept(content)
            except PdfRejected as error:
                return self._ingestion_failure(run_id, error.code, error.safe_message)
            total_pages += page_count
            if total_pages > self._settings.max_total_pages:
                return self._ingestion_failure(run_id, "BATCH_LIMIT_EXCEEDED", "The PDF bundle exceeds its page limit.")

            paths = sorted(paths_by_digest[digest], key=lambda item: (item.name, str(item)))
            entry = DocumentManifestEntry(
                document_id=f"sha256:{digest}",
                original_filename=paths[0].name,
                sha256=digest,
                byte_size=len(content),
                page_count=page_count,
                duplicate_filenames=tuple(path.name for path in paths[1:]),
            )
            accepted.append(AcceptedDocument(path=paths[0], content=content, manifest_entry=entry))

        entries = tuple(document.manifest_entry for document in accepted)
        manifest = DocumentManifest(
            manifest_version="1.0",
            documents=entries,
            total_bytes=sum(entry.byte_size for entry in entries),
            total_pages=sum(entry.page_count for entry in entries),
        )
        return manifest, tuple(accepted)

    @staticmethod
    def _ingestion_failure(run_id: str, code: str, safe_message: str) -> ExtractionFailed:
        return _failure(
            run_id=run_id,
            stage=FailureStage.PDF_INGESTION,
            code=code,
            safe_message=safe_message,
            retryable=False,
        )

    @staticmethod
    def _extraction_failure(
        run_id: str,
        code: str,
        safe_message: str,
        *,
        retryable: bool,
    ) -> ExtractionFailed:
        return _failure(
            run_id=run_id,
            stage=FailureStage.EXTRACTION,
            code=code,
            safe_message=safe_message,
            retryable=retryable,
        )


def _provider_result_is_retryable(result: object) -> bool:
    if isinstance(result, ProviderIncomplete):
        return result.reason is IncompleteReason.MAX_OUTPUT_TOKENS
    if isinstance(result, ProviderFailed):
        return result.category in RETRYABLE_PROVIDER_CATEGORIES
    return False


def _provider_failure(run_id: str, result: object, *, retryable: bool) -> ExtractionFailed:
    if isinstance(result, ProviderRefused):
        code = "EXTRACTION_REFUSED"
        message = "The extraction provider refused the application-facts request."
    elif isinstance(result, ProviderIncomplete):
        code = "EXTRACTION_INCOMPLETE"
        message = "The extraction provider did not complete the structured application facts."
    elif isinstance(result, ProviderFailed):
        code = _provider_error_code(result.category)
        message = "The extraction provider could not return structured application facts."
    else:
        code = "EXTRACTION_INVALID_OUTPUT"
        message = "The extraction provider did not return valid structured application facts."
        retryable = False
    return _failure(
        run_id=run_id,
        stage=FailureStage.EXTRACTION,
        code=code,
        safe_message=message,
        retryable=retryable,
    )


def _provider_error_code(category: ProviderErrorCategory) -> str:
    if category in RETRYABLE_PROVIDER_CATEGORIES:
        return "EXTRACTION_UNAVAILABLE"
    return {
        ProviderErrorCategory.AUTHENTICATION: "EXTRACTION_AUTHENTICATION_FAILED",
        ProviderErrorCategory.PERMISSION: "EXTRACTION_PERMISSION_DENIED",
        ProviderErrorCategory.MODEL_UNAVAILABLE: "EXTRACTION_MODEL_UNAVAILABLE",
        ProviderErrorCategory.INVALID_REQUEST: "EXTRACTION_INVALID_REQUEST",
        ProviderErrorCategory.INVALID_OUTPUT: "EXTRACTION_INVALID_OUTPUT",
        ProviderErrorCategory.UNKNOWN: "EXTRACTION_FAILED",
    }[category]


def _attempt_metadata(
    result: object,
    *,
    attempt_number: int,
    model_requested: str,
) -> ProviderAttemptMetadata:
    if isinstance(result, ProviderRefused):
        return ProviderAttemptMetadata(
            operation="EXTRACTION",
            attempt_number=attempt_number,
            model_requested=model_requested,
            response_status="REFUSED",
            request_id=result.request_id,
            error_category="REFUSAL",
            duration_ms=result.duration_ms,
        )
    if isinstance(result, ProviderIncomplete):
        return ProviderAttemptMetadata(
            operation="EXTRACTION",
            attempt_number=attempt_number,
            model_requested=model_requested,
            response_status="INCOMPLETE",
            request_id=result.request_id,
            error_category=result.reason.value,
            duration_ms=result.duration_ms,
        )
    if isinstance(result, ProviderFailed):
        return ProviderAttemptMetadata(
            operation="EXTRACTION",
            attempt_number=attempt_number,
            model_requested=model_requested,
            response_status="FAILED",
            request_id=result.request_id,
            error_category=result.category.value,
            duration_ms=result.duration_ms,
        )
    return ProviderAttemptMetadata(
        operation="EXTRACTION",
        attempt_number=attempt_number,
        model_requested=model_requested,
        response_status="INVALID_OUTPUT",
        error_category="INVALID_OUTPUT",
        duration_ms=0,
    )


def _failure(
    *,
    run_id: str,
    stage: FailureStage,
    code: str,
    safe_message: str,
    retryable: bool,
) -> ExtractionFailed:
    return ExtractionFailed(
        kind="EXTRACTION_FAILED",
        failure=ProcessingFailureReport(
            kind="PROCESSING_FAILURE",
            report_version="1.0",
            run_id=run_id,
            stage=stage,
            code=code,
            safe_message=safe_message,
            retryable=retryable,
        ),
    )
