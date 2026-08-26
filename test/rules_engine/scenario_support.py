from typing import Any

from app.models.artifacts import ApplicationFactsArtifact

DOCUMENT_DIGEST = "a" * 64
DOCUMENT_ID = f"sha256:{DOCUMENT_DIGEST}"


def make_artifact(scenario: dict[str, Any]) -> ApplicationFactsArtifact:
    """Build one strict schema-2 artifact from a concise reviewed scenario."""
    scenario_id = str(scenario["id"])
    school = () if "school" not in scenario else (_school(scenario_id, scenario["school"]),)
    advanced = () if "advanced" not in scenario else (_advanced(scenario_id, scenario["advanced"]),)
    professional = (
        () if "professional" not in scenario else (_professional(scenario_id, scenario["professional"]),)
    )
    return ApplicationFactsArtifact.model_validate(
        {
            "kind": "APPLICATION_FACTS",
            "artifact_version": "2.0",
            "run_id": f"run-scenario-{scenario_id}",
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
                        "document_id": DOCUMENT_ID,
                        "original_filename": f"scenario-{scenario_id}.pdf",
                        "sha256": DOCUMENT_DIGEST,
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
                "school_qualifications": school,
                "advanced_vocational_qualifications": advanced,
                "professional_access_candidates": professional,
            },
            "versions": {
                "extraction_prompt": "application-facts/2.0-fixture",
                "model_requested": "fixture-model",
                "model_returned": "fixture-model",
            },
            "attempts": [],
            "warnings": [],
        }
    )


def candidate_id(scenario_id: str, candidate: str) -> str:
    """Return the deterministic entity identifier used by one fixture."""
    return {
        "school": f"school-{scenario_id}",
        "advanced": f"advanced-{scenario_id}",
        "professional": f"professional-{scenario_id}",
    }[candidate]


def _known_or_unknown(fact_id: str, raw: Any, default: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"state": "KNOWN", "fact_id": fact_id, "value": raw, "evidence": []}
    state = raw.get("state", "KNOWN")
    if state == "KNOWN":
        return {"state": "KNOWN", "fact_id": fact_id, "value": raw.get("value", default), "evidence": []}
    if state == "MISSING":
        return {"state": "MISSING", "fact_id": fact_id, "evidence": []}
    if state == "UNREADABLE":
        return {
            "state": "UNREADABLE",
            "fact_id": fact_id,
            "evidence": [{"document_id": DOCUMENT_ID, "page_number": 1, "excerpt": "unreadable"}],
        }
    if state == "CONFLICTING":
        return {
            "state": "CONFLICTING",
            "fact_id": fact_id,
            "candidates": [{"value": value, "evidence": []} for value in raw["values"]],
        }
    raise ValueError(f"Unsupported fixture fact state: {state}")


def _school(scenario_id: str, values: dict[str, Any]) -> dict[str, Any]:
    entity = f"school-{scenario_id}"
    defaults = {
        "type": "OTHER",
        "country": "DE",
        "completed": True,
        "access_scope": "GENERAL",
        "validity_restriction_present": False,
        "validity_restriction_code": "OTHER",
        "school_part_proven": True,
        "vocational_part_proven": True,
        "issuing_region": "DACH",
    }
    return {
        "qualification_id": entity,
        **{
            field: _known_or_unknown(f"{entity}.{field}", values.get(field, default), default)
            for field, default in defaults.items()
        },
    }


def _advanced(scenario_id: str, values: dict[str, Any]) -> dict[str, Any]:
    entity = f"advanced-{scenario_id}"
    defaults = {
        "type": "OTHER",
        "country": "DE",
        "completed": True,
        "dqr_or_eqr_level": 6,
        "teaching_hours": 400,
        "builds_on_completed_training": True,
        "builds_on_recognized_training": True,
    }
    return {
        "qualification_id": entity,
        **{
            field: _known_or_unknown(f"{entity}.{field}", values.get(field, default), default)
            for field, default in defaults.items()
        },
    }


def _professional(scenario_id: str, values: dict[str, Any]) -> dict[str, Any]:
    candidate = f"professional-{scenario_id}"
    training = f"training-{scenario_id}"
    training_defaults = {
        "type": "VOCATIONAL_TRAINING",
        "country": "DE",
        "completed": True,
        "recognized": True,
        "duration_months": 24,
        "dqr_or_eqr_level": 4,
        "subject": "Computer science",
    }
    candidate_defaults = {
        "all_period_dates_known": True,
        "all_weekly_hours_known": True,
        "mini_job_classification_complete": True,
        "full_time_equivalent_days_after_training": 1095,
        "professional_fields_after_training": ["Software development"],
        "subject_relationship": "MATCH",
    }
    return {
        "candidate_id": candidate,
        "training": {
            "training_id": training,
            **{
                field: _known_or_unknown(f"{candidate}.training.{field}", values.get(field, default), default)
                for field, default in training_defaults.items()
            },
        },
        "employment_period_ids": [f"employment-{scenario_id}"],
        **{
            field: _known_or_unknown(f"{candidate}.{field}", values.get(field, default), default)
            for field, default in candidate_defaults.items()
        },
    }
