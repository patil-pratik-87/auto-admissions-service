import pytest
from pydantic import ValidationError

from app.models.facts import ApplicationFacts, ConflictingFact, EvidenceRef, KnownFact


def _evidence(excerpt: str) -> dict[str, object]:
    return {
        "document_id": "sha256:" + "a" * 64,
        "page_number": 1,
        "excerpt": excerpt,
    }


def _known(fact_id: str, value: object, excerpt: str | None = None) -> dict[str, object]:
    return {
        "state": "KNOWN",
        "fact_id": fact_id,
        "value": value,
        "evidence": [] if excerpt is None else [_evidence(excerpt)],
    }


def _missing(fact_id: str) -> dict[str, object]:
    return {"state": "MISSING", "fact_id": fact_id, "evidence": []}


def test_application_facts_round_trip_preserves_direct_known_false_and_missing() -> None:
    """Direct model output keeps an explicit false value distinct from absence."""
    payload = {
        "schema_version": "2.0",
        "school_qualifications": [
            {
                "qualification_id": "school-001",
                "type": _known("school-001.type", "ALLGEMEINE_HOCHSCHULREIFE"),
                "country": _known("school-001.country", "DE", "Bundesrepublik Deutschland"),
                "completed": _known("school-001.completed", True, "bestanden"),
                "access_scope": _known("school-001.access_scope", "GENERAL"),
                "validity_restriction_present": _known(
                    "school-001.validity_restriction_present", False
                ),
                "validity_restriction_code": _missing("school-001.validity_restriction_code"),
                "school_part_proven": _missing("school-001.school_part_proven"),
                "vocational_part_proven": _missing("school-001.vocational_part_proven"),
                "issuing_region": _known("school-001.issuing_region", "DACH"),
            }
        ],
        "advanced_vocational_qualifications": [],
        "professional_access_candidates": [],
    }

    facts = ApplicationFacts.model_validate(payload)
    restored = ApplicationFacts.model_validate_json(facts.model_dump_json())

    qualification = restored.school_qualifications[0]
    assert qualification.validity_restriction_present.state == "KNOWN"
    assert qualification.validity_restriction_present.value is False
    assert qualification.validity_restriction_code.state == "MISSING"
    assert restored == facts


def test_known_fact_does_not_require_evidence() -> None:
    """Strict structured output is accepted without claiming local verification."""
    fact = KnownFact[bool](state="KNOWN", fact_id="candidate.completed", value=False)

    assert fact.value is False
    assert fact.evidence == ()


def test_evidence_reference_has_no_verification_claim() -> None:
    """Evidence is an LLM-reported pointer, not a runtime-verified assertion."""
    reference = EvidenceRef.model_validate(_evidence("bestanden"))

    assert "verification" not in type(reference).model_fields
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        EvidenceRef.model_validate({**_evidence("bestanden"), "verification": "VERIFIED"})


def test_conflicting_fact_requires_distinct_values_but_not_verified_evidence() -> None:
    """A conflict is structural and may contain model-reported or empty evidence."""
    with pytest.raises(ValidationError, match="distinct values"):
        ConflictingFact[str].model_validate(
            {
                "state": "CONFLICTING",
                "fact_id": "school-001.country",
                "candidates": [
                    {"value": "DE", "evidence": []},
                    {"value": "DE", "evidence": []},
                ],
            }
        )


def test_application_facts_reject_duplicate_entity_and_fact_ids() -> None:
    """Final model output cannot make deterministic selection ambiguous."""
    qualification = {
        "qualification_id": "school-001",
        "type": _missing("duplicate.fact"),
        "country": _missing("duplicate.fact"),
        "completed": _missing("school-001.completed"),
        "access_scope": _missing("school-001.access_scope"),
        "validity_restriction_present": _missing("school-001.restriction"),
        "validity_restriction_code": _missing("school-001.restriction_code"),
        "school_part_proven": _missing("school-001.school_part"),
        "vocational_part_proven": _missing("school-001.vocational_part"),
        "issuing_region": _missing("school-001.region"),
    }

    with pytest.raises(ValidationError, match="fact identifiers must be unique"):
        ApplicationFacts.model_validate(
            {
                "schema_version": "2.0",
                "school_qualifications": [qualification],
                "advanced_vocational_qualifications": [],
                "professional_access_candidates": [],
            }
        )
