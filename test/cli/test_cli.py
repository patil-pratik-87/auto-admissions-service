import json
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app
from app.models.artifacts import ApplicationFactsArtifact, FactsArtifactVersions
from app.models.documents import DocumentManifest, DocumentManifestEntry
from app.models.facts import ApplicationFacts
from app.models.programs import PolicyRef, ProgramContext


def _artifact() -> ApplicationFactsArtifact:
    digest = "a" * 64
    return ApplicationFactsArtifact(
        kind="APPLICATION_FACTS",
        artifact_version="2.0",
        run_id="offline-replay",
        program=ProgramContext(
            catalog_version="0.1",
            program_id="BACHELOR",
            display_name="Bachelor's Study Program",
            study_level="BACHELOR",
            program_subject="COMPUTER_SCIENCE",
            policy=PolicyRef(id="IU_BACHELOR_ACCESS", version="0.0.22"),
        ),
        manifest=DocumentManifest(
            manifest_version="1.0",
            documents=(
                DocumentManifestEntry(
                    document_id=f"sha256:{digest}",
                    original_filename="fixture.pdf",
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
            extraction_prompt="application-facts/2.0",
            model_requested="fixture-model",
            model_returned="fixture-model",
        ),
    )


def test_cli_exposes_extract_evaluate_and_screen() -> None:
    """The installed entry point presents the three accepted operations."""
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "extract" in result.stdout
    assert "evaluate" in result.stdout
    assert "screen" in result.stdout


def test_cli_evaluate_replays_facts_offline_without_openai_key(tmp_path: Path) -> None:
    """Deterministic evaluation neither requires nor initializes OpenAI."""
    facts_path = tmp_path / "application-facts.json"
    facts_path.write_text(_artifact().model_dump_json(), encoding="utf-8")
    result_path = tmp_path / "application-result.json"

    result = CliRunner().invoke(
        app,
        [
            "evaluate",
            "--facts",
            str(facts_path),
            "--output",
            str(result_path),
            "--quiet",
        ],
        env={"OPENAI_API_KEY": None, "ADMISSIONS_OPENAI_API_KEY": None},
    )

    assert result.exit_code == 0, result.output
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["run_id"] == "offline-replay"
    assert result["application_status"] == "MANUAL_REVIEW"
    assert len(result["rules"]) == 5


def test_cli_extract_requires_openai_credentials_before_processing(tmp_path: Path) -> None:
    """A missing credential is configuration failure, not an applicant result."""
    pdf_path = tmp_path / "fixture.pdf"
    pdf_path.write_bytes(b"%PDF-1.7 fixture")

    result = CliRunner().invoke(
        app,
        [
            "extract",
            str(pdf_path),
            "--program",
            "BACHELOR",
            "--output",
            str(tmp_path / "facts.json"),
            "--quiet",
        ],
        env={"OPENAI_API_KEY": None, "ADMISSIONS_OPENAI_API_KEY": None},
    )

    assert result.exit_code == 2
    assert "OPENAI_API_KEY" in result.output
    assert not (tmp_path / "facts.json").exists()
