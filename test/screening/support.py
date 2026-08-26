"""Independent frozen examples used through screening seams."""

from pathlib import Path

from app.models.artifacts import (
    ApplicationFactsArtifact,
    FactsArtifactVersions,
)
from app.models.documents import DocumentManifest, DocumentManifestEntry
from app.models.facts import ApplicationFacts
from app.models.programs import PolicyRef, ProgramCatalog, ProgramContext, ProgramDefinition
from app.models.results import (
    RULE_ORDER,
    ApplicationResult,
    ApplicationStatus,
    CanonicalSummary,
    ProgramRef,
    ResultSummary,
    RuleResult,
    RuleStatus,
)


def program_catalog() -> ProgramCatalog:
    """Return the single trusted catalog from the accepted specification."""
    return ProgramCatalog(
        catalog_version="0.1",
        programs=(
            ProgramDefinition(
                id="BACHELOR",
                display_name="Bachelor's Study Program",
                study_level="BACHELOR",
                program_subject="COMPUTER_SCIENCE",
                policy=PolicyRef(id="IU_BACHELOR_ACCESS", version="0.0.22"),
            ),
        ),
    )


def program_context() -> ProgramContext:
    """Return the resolved trusted program example."""
    return program_catalog().resolve("BACHELOR")


def facts_artifact(*, run_id: str = "run-fixed", program: ProgramContext | None = None) -> ApplicationFactsArtifact:
    """Return a minimal complete facts artifact with reviewed literal values."""
    digest = "a" * 64
    return ApplicationFactsArtifact(
        kind="APPLICATION_FACTS",
        artifact_version="2.0",
        run_id=run_id,
        program=program or program_context(),
        manifest=DocumentManifest(
            manifest_version="1.0",
            documents=(
                DocumentManifestEntry(
                    document_id=f"sha256:{digest}",
                    original_filename="synthetic.pdf",
                    sha256=digest,
                    byte_size=12,
                    page_count=1,
                ),
            ),
            total_bytes=12,
            total_pages=1,
        ),
        facts=ApplicationFacts(
            schema_version="2.0",
            school_qualifications=(),
            advanced_vocational_qualifications=(),
            professional_access_candidates=(),
        ),
        versions=FactsArtifactVersions(
            extraction_prompt="extract-v1",
            model_requested="gpt-test",
            model_returned="gpt-test",
        ),
    )


def application_result(*, run_id: str = "run-fixed") -> ApplicationResult:
    """Return a complete deterministic ineligible result for CLI/runtime tests."""
    rules = tuple(
        RuleResult(
            rule_id=rule_id,
            status=RuleStatus.NOT_APPLICABLE,
            reason_code="NO_CANDIDATE_FOR_RULE",
            candidate_ids=(),
            fact_ids=(),
            evidence_ids=(),
            condition=None,
        )
        for rule_id in RULE_ORDER
    )
    return ApplicationResult(
        kind="APPLICATION_RESULT",
        result_version="2.0",
        run_id=run_id,
        scope="ACADEMIC_ACCESS_ONLY",
        program=ProgramRef(id="BACHELOR", display_name="Bachelor's Study Program"),
        policy=PolicyRef(id="IU_BACHELOR_ACCESS", version="0.0.22"),
        application_status=ApplicationStatus.INELIGIBLE,
        application_reason_code="NO_RECOGNIZED_ADMISSIONS_RULE",
        rules=rules,
        missing_information=(),
        manual_review=(),
        warnings=(),
        evidence=(),
        summary=ResultSummary(
            canonical=CanonicalSummary(
                headline="Academic access was not established",
                explanation="No supported admissions rule was established from the supplied facts.",
                required_information=(),
            ),
            llm_paraphrase=None,
        ),
    )


class FixedRunIds:
    """Return deterministic operation identifiers."""

    def __init__(self, *run_ids: str) -> None:
        self._run_ids = iter(run_ids)

    def __call__(self) -> str:
        """Return the next configured identifier."""
        return next(self._run_ids)


def synthetic_pdf_path(tmp_path: Path) -> Path:
    """Create a path token for scripted facts extractors.

    The runtime does not inspect input PDFs itself; the Facts extractor owns that
    boundary. The file is intentionally not a real PDF in these seam tests.
    """
    return tmp_path / "synthetic.pdf"
