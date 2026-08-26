from pathlib import Path
from shutil import copytree

import pytest

from app.models.artifacts import ApplicationFactsArtifact


@pytest.fixture
def empty_artifact() -> ApplicationFactsArtifact:
    digest = "a" * 64
    return ApplicationFactsArtifact.model_validate(
        {
            "kind": "APPLICATION_FACTS",
            "artifact_version": "2.0",
            "run_id": "run-decision-001",
            "program": {
                "catalog_version": "0.1",
                "program_id": "BACHELOR",
                "display_name": "Bachelor's Study Program",
                "study_level": "BACHELOR",
                "program_subject": "COMPUTER_SCIENCE",
                "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
            },
            "manifest": {
                "manifest_version": "1.0",
                "documents": [
                    {
                        "document_id": f"sha256:{digest}",
                        "original_filename": "candidate.pdf",
                        "sha256": digest,
                        "byte_size": 100,
                        "page_count": 1,
                        "duplicate_filenames": [],
                    }
                ],
                "total_bytes": 100,
                "total_pages": 1,
            },
            "facts": {
                "schema_version": "2.0",
                "school_qualifications": [],
                "advanced_vocational_qualifications": [],
                "professional_access_candidates": [],
            },
            "versions": {
                "extraction_prompt": "application-facts/2.0",
                "model_requested": "fixture-model",
                "model_returned": "fixture-model",
            },
            "attempts": [],
            "warnings": [],
        }
    )


@pytest.fixture
def rules_root() -> Path:
    return Path(__file__).parents[2] / "rules"


@pytest.fixture
def copied_rules(rules_root: Path, tmp_path: Path) -> Path:
    destination = tmp_path / "rules"
    copytree(rules_root, destination)
    return destination
