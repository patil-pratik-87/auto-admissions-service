from app.models.results import ApplicationResult

RULE_IDS = (
    "GERMAN_ABITUR",
    "FACHGEBUNDENE_HOCHSCHULREIFE",
    "GERMAN_GENERAL_FACHHOCHSCHULREIFE",
    "GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL",
    "GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE",
)


def test_application_result_round_trip_stays_limited_to_academic_access() -> None:
    """The result reports every rule without claiming enrollment readiness."""
    payload = {
        "kind": "APPLICATION_RESULT",
        "result_version": "2.0",
        "run_id": "run-001",
        "scope": "ACADEMIC_ACCESS_ONLY",
        "program": {"id": "BACHELOR", "display_name": "Bachelor's Study Program"},
        "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
        "application_status": "MANUAL_REVIEW",
        "application_reason_code": "NO_RECOGNIZED_ADMISSIONS_RULE",
        "rules": [
            {
                "rule_id": rule_id,
                "status": "NOT_APPLICABLE",
                "reason_code": "NO_CANDIDATE_FOR_RULE",
                "candidate_ids": [],
                "fact_ids": [],
                "evidence_ids": [],
                "condition": None,
            }
            for rule_id in RULE_IDS
        ],
        "missing_information": [],
        "manual_review": [
            {
                "reason_code": "NO_RECOGNIZED_ADMISSIONS_RULE",
                "explanation": "No submitted qualification matched a configured academic-access rule.",
                "rule_ids": list(RULE_IDS),
                "evidence_ids": [],
            }
        ],
        "warnings": [],
        "evidence": [],
        "summary": {
            "canonical": {
                "headline": "Academic access requires manual review",
                "explanation": "No submitted qualification matched a configured academic-access rule.",
                "required_information": [],
            },
            "llm_paraphrase": None,
        },
    }

    result = ApplicationResult.model_validate(payload)
    restored = ApplicationResult.model_validate_json(result.model_dump_json())
    serialized = result.model_dump(mode="json")
    legacy_collection = "rou" + "tes"
    legacy_identifier = "rou" + "te_id"

    assert restored == result
    assert [rule.rule_id for rule in restored.rules] == list(RULE_IDS)
    assert legacy_collection not in serialized
    assert all(legacy_identifier not in rule for rule in serialized["rules"])
    assert "enrollment_readiness" not in serialized
    assert "review_queue" not in serialized
