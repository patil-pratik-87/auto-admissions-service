from app.models.facts import ApplicationFacts
from app.models.programs import ProgramContext
from app.services import ports
from app.services.ports import (
    ExtractApplicationFactsRequest,
    PdfModelInput,
    ProviderSucceeded,
)


def _program() -> ProgramContext:
    return ProgramContext.model_validate(
        {
            "catalog_version": "0.1",
            "program_id": "BACHELOR",
            "display_name": "Bachelor's Study Program",
            "study_level": "BACHELOR",
            "program_subject": "COMPUTER_SCIENCE",
            "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
        }
    )


def test_extraction_request_contains_complete_bundle_and_trusted_program() -> None:
    """The single extraction operation has everything needed for final facts."""
    request = ExtractApplicationFactsRequest(
        documents=(
            PdfModelInput(
                document_id="sha256:" + "a" * 64,
                filename="qualification.pdf",
                content=b"%PDF-1.7 fixture",
            ),
        ),
        program=_program(),
        model="gpt-5.4-mini",
        prompt_version="application-facts/2.0",
        max_output_tokens=8_000,
    )

    assert request.program.program_id == "BACHELOR"
    assert request.documents[0].content.startswith(b"%PDF")


def test_successful_extraction_output_is_application_facts_directly() -> None:
    """There is no intermediate observation or subject-assessment payload."""
    facts = ApplicationFacts(
        schema_version="2.0",
        school_qualifications=(),
        advanced_vocational_qualifications=(),
        professional_access_candidates=(),
    )

    result = ProviderSucceeded[ApplicationFacts](
        kind="SUCCEEDED",
        output=facts,
        model_returned="gpt-5.4-mini",
        usage={"input_tokens": 10, "output_tokens": 20},
        duration_ms=30,
    )

    assert result.output is facts


def test_discarded_draft_and_subject_types_are_not_public_ports() -> None:
    """The model boundary cannot accidentally revive the verification pipeline."""
    discarded = {
        "ObservationBundleDraft",
        "ObservedDraft",
        "NotFoundDraft",
        "UnreadableDraft",
        "DraftFact",
        "UnverifiedEvidenceRef",
        "SubjectAssessmentRequest",
        "SubjectAssessmentDraft",
        "SubjectProviderResult",
    }

    assert discarded.isdisjoint(vars(ports))
