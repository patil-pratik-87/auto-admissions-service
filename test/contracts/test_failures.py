import pytest
from pydantic import ValidationError

from app.models.failures import FailureStage, ProcessingFailureReport


def test_processing_failure_cannot_contain_an_applicant_outcome() -> None:
    """Technical failure must remain structurally distinct from evaluation."""
    with pytest.raises(ValidationError, match="application_status"):
        ProcessingFailureReport.model_validate(
            {
                "kind": "PROCESSING_FAILURE",
                "report_version": "1.0",
                "run_id": "run-001",
                "stage": "EXTRACTION",
                "code": "EXTRACTION_REFUSED",
                "safe_message": "The extraction request was refused.",
                "retryable": False,
                "application_status": "INELIGIBLE",
            }
        )


def test_failure_stages_match_the_direct_facts_pipeline() -> None:
    """Discarded verification, derivation, and subject calls cannot reappear."""
    assert FailureStage.FACTS_VALIDATION == "FACTS_VALIDATION"
    assert {
        "EVIDENCE_VERIFICATION",
        "DERIVATION",
        "SUBJECT_ASSESSMENT",
        "FACTS_ASSEMBLY",
    }.isdisjoint(FailureStage.__members__)
