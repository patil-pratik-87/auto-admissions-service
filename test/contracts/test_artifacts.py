import pytest
from pydantic import ValidationError

from app.models.artifacts import ApplicationFactsArtifact


def _payload() -> dict[str, object]:
    digest = "a" * 64
    return {
        "kind": "APPLICATION_FACTS",
        "artifact_version": "2.0",
        "run_id": "run-001",
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
                    "original_filename": "certificate.pdf",
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
            "model_requested": "gpt-5.4-mini",
            "model_returned": "gpt-5.4-mini",
        },
        "attempts": [],
        "warnings": [],
    }


def test_facts_artifact_round_trip_keeps_replay_inputs_without_redundant_hashes() -> None:
    """The saved artifact is the complete and readable deterministic replay input."""
    artifact = ApplicationFactsArtifact.model_validate(_payload())
    restored = ApplicationFactsArtifact.model_validate_json(artifact.model_dump_json())
    serialized_keys = artifact.model_dump(mode="json").keys()

    assert restored == artifact
    assert "bundle_sha256" not in serialized_keys
    assert "application_facts_sha256" not in serialized_keys
    assert "document_manifest_sha256" not in serialized_keys


@pytest.mark.parametrize(
    ("document_id", "page_number", "message"),
    [
        ("sha256:" + "b" * 64, 1, "unknown document"),
        ("sha256:" + "a" * 64, 2, "outside the document"),
    ],
)
def test_facts_artifact_rejects_evidence_outside_the_manifest(
    document_id: str,
    page_number: int,
    message: str,
) -> None:
    """Reference bounds are structural integrity checks, not factual verification."""
    payload = _payload()
    payload["facts"] = {
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
                "country": {"state": "MISSING", "fact_id": "school-001.country", "evidence": []},
                "completed": {"state": "MISSING", "fact_id": "school-001.completed", "evidence": []},
                "access_scope": {"state": "MISSING", "fact_id": "school-001.scope", "evidence": []},
                "validity_restriction_present": {
                    "state": "MISSING",
                    "fact_id": "school-001.restriction",
                    "evidence": [],
                },
                "validity_restriction_code": {
                    "state": "MISSING",
                    "fact_id": "school-001.restriction-code",
                    "evidence": [],
                },
                "school_part_proven": {
                    "state": "MISSING",
                    "fact_id": "school-001.school-part",
                    "evidence": [],
                },
                "vocational_part_proven": {
                    "state": "MISSING",
                    "fact_id": "school-001.vocational-part",
                    "evidence": [],
                },
                "issuing_region": {
                    "state": "MISSING",
                    "fact_id": "school-001.region",
                    "evidence": [],
                },
            }
        ],
        "advanced_vocational_qualifications": [],
        "professional_access_candidates": [],
    }

    with pytest.raises(ValidationError, match=message):
        ApplicationFactsArtifact.model_validate(payload)
