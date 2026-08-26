from hashlib import sha256
from pathlib import Path

from app.facts import FactsExtractor
from app.interface import ScreenCompleted, ScreenRequest
from app.models.facts import ApplicationFacts
from app.models.programs import PolicyRef, ProgramCatalog, ProgramDefinition
from app.rules_engine import RulesEngine
from app.services.ports import (
    ExtractApplicationFactsRequest,
    ExtractionProviderResult,
    ParaphraseProviderResult,
    ParaphraseRequest,
    ProviderSucceeded,
    ProviderUsage,
)
from app.services.screening import ScreeningConfig, ScreeningWorkflow


def _known(fact_id: str, value: object) -> dict[str, object]:
    return {"state": "KNOWN", "fact_id": fact_id, "value": value, "evidence": []}


def _missing(fact_id: str) -> dict[str, object]:
    return {"state": "MISSING", "fact_id": fact_id, "evidence": []}


def _abitur_facts() -> ApplicationFacts:
    return ApplicationFacts.model_validate(
        {
            "schema_version": "2.0",
            "school_qualifications": [
                {
                    "qualification_id": "school-demo",
                    "type": _known("school-demo.type", "ALLGEMEINE_HOCHSCHULREIFE"),
                    "country": _known("school-demo.country", "DE"),
                    "completed": _known("school-demo.completed", True),
                    "access_scope": _known("school-demo.access_scope", "GENERAL"),
                    "validity_restriction_present": _known("school-demo.restriction", False),
                    "validity_restriction_code": _missing("school-demo.restriction-code"),
                    "school_part_proven": _missing("school-demo.school-part"),
                    "vocational_part_proven": _missing("school-demo.vocational-part"),
                    "issuing_region": _known("school-demo.region", "DACH"),
                }
            ],
            "advanced_vocational_qualifications": [],
            "professional_access_candidates": [],
        }
    )


class _OneCallModel:
    def __init__(self, facts: ApplicationFacts) -> None:
        self.facts = facts
        self.requests: list[ExtractApplicationFactsRequest] = []

    def extract_application_facts(self, request: ExtractApplicationFactsRequest) -> ExtractionProviderResult:
        self.requests.append(request)
        return ProviderSucceeded[ApplicationFacts](
            kind="SUCCEEDED",
            output=self.facts,
            model_returned="fixture-model",
            usage=ProviderUsage(input_tokens=100, output_tokens=200),
            duration_ms=1,
        )

    def paraphrase_summary(self, request: ParaphraseRequest) -> ParaphraseProviderResult:
        del request
        raise AssertionError("Paraphrasing is disabled in the core screen flow")


class _FixedRunId:
    def __call__(self) -> str:
        return "run-offline-end-to-end"


def test_real_pdf_to_saved_facts_to_zero_steiner_decision(tmp_path: Path) -> None:
    """The full core flow needs one extraction call and no evaluator model call."""
    pdf_path = Path("samples/filled-documents/sofia-lorenz/abitur-zeugnis.pdf")
    model = _OneCallModel(_abitur_facts())
    catalog = ProgramCatalog(
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
    screening = ScreeningWorkflow(
        catalog=catalog,
        facts_extractor=FactsExtractor(model=model),
        rules_engine=RulesEngine.activate(Path("rules")),
        model_port=model,
        run_id_factory=_FixedRunId(),
        config=ScreeningConfig(default_model="fixture-model"),
    )

    outcome = screening.screen(
        ScreenRequest(
            program_id="BACHELOR",
            pdf_paths=(pdf_path,),
            output_dir=tmp_path / "screen",
        )
    )

    assert isinstance(outcome, ScreenCompleted)
    assert outcome.result.application_status == "ELIGIBLE"
    assert outcome.result.application_reason_code == "ACADEMIC_ACCESS_ELIGIBLE"
    assert outcome.facts_path.is_file()
    assert outcome.result_path.is_file()
    assert outcome.artifact.facts == model.facts
    assert len(model.requests) == 1
    assert model.requests[0].documents[0].document_id == (
        f"sha256:{sha256(pdf_path.read_bytes()).hexdigest()}"
    )
