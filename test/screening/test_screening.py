"""Behavior tests for the synchronous admissions screening workflow."""

from pathlib import Path

from app.interface import (
    EvaluateCompleted,
    EvaluateRequest,
    ExtractCompleted,
    ExtractRequest,
    RunFailed,
    ScreenCompleted,
    ScreenRequest,
)
from app.models.artifacts import ApplicationFactsArtifact
from app.models.failures import FailureStage
from app.models.outcomes import EvaluationOutcome, EvaluationSucceeded, ExtractionSucceeded
from app.models.programs import ProgramContext
from app.services.ports import (
    ParaphraseDraft,
    ParaphraseRequest,
    ProviderRefused,
    ProviderSucceeded,
    ProviderUsage,
)
from app.services.screening import ScreeningConfig, ScreeningWorkflow

from .support import FixedRunIds, application_result, facts_artifact, program_catalog


class SuccessfulFactsExtractor:
    """Script the deep facts boundary with a complete artifact."""

    def extract(
        self,
        *,
        run_id: str,
        program: ProgramContext,
        pdf_paths: tuple[Path, ...],
        model_override: str | None,
    ) -> ExtractionSucceeded:
        """Return a valid artifact using the application-owned run and program."""
        del pdf_paths, model_override
        return ExtractionSucceeded(
            kind="EXTRACTION_SUCCEEDED",
            artifact=facts_artifact(run_id=run_id, program=program),
        )


class UnusedRulesEngine:
    """Guard the unrelated rules engine boundary in extraction tests."""

    def evaluate(self, artifact: ApplicationFactsArtifact) -> EvaluationOutcome:
        """Fail if extraction crosses into deterministic evaluation."""
        del artifact
        raise AssertionError("Rules engine must not run during extract")


class UnusedFactsExtractor:
    """Guard the unrelated facts boundary in evaluation tests."""

    def extract(
        self,
        *,
        run_id: str,
        program: ProgramContext,
        pdf_paths: tuple[Path, ...],
        model_override: str | None,
    ) -> ExtractionSucceeded:
        """Fail if saved-facts evaluation starts document extraction."""
        del run_id, program, pdf_paths, model_override
        raise AssertionError("Facts extractor must not run during evaluate")


class SuccessfulRulesEngine:
    """Script the pure rules engine boundary with a deterministic result."""

    def evaluate(self, artifact: ApplicationFactsArtifact) -> EvaluationOutcome:
        """Return a result that preserves the saved application run identity."""
        return EvaluationSucceeded(
            kind="EVALUATION_SUCCEEDED",
            result=application_result(run_id=artifact.run_id),
        )


class ReloadRequiredRulesEngine:
    """Accept only an artifact reconstructed from the persistence boundary."""

    def __init__(self, in_memory_artifact: ApplicationFactsArtifact) -> None:
        self._in_memory_artifact = in_memory_artifact

    def evaluate(self, artifact: ApplicationFactsArtifact) -> EvaluationOutcome:
        """Require equal content but a distinct validated model instance."""
        if artifact is self._in_memory_artifact or artifact != self._in_memory_artifact:
            raise AssertionError("screen must reload the exact serialized facts artifact")
        return EvaluationSucceeded(
            kind="EVALUATION_SUCCEEDED",
            result=application_result(run_id=artifact.run_id),
        )


def test_extract_persists_the_complete_facts_artifact(tmp_path: Path) -> None:
    """Extraction returns the exact artifact that can be loaded from its path."""
    output_path = tmp_path / "nested" / "application-facts.json"
    screening = ScreeningWorkflow(
        catalog=program_catalog(),
        facts_extractor=SuccessfulFactsExtractor(),
        rules_engine=UnusedRulesEngine(),
        model_port=None,
        run_id_factory=FixedRunIds("run-extract"),
        config=ScreeningConfig(default_model="gpt-test"),
    )

    outcome = screening.extract(
        ExtractRequest(
            program_id="BACHELOR",
            pdf_paths=(tmp_path / "synthetic.pdf",),
            output_path=output_path,
        )
    )

    assert isinstance(outcome, ExtractCompleted)
    assert outcome.facts_path == output_path
    assert outcome.artifact == facts_artifact(run_id="run-extract")
    assert output_path.read_text(encoding="utf-8").endswith("\n")


def test_evaluate_replays_saved_facts_without_a_model_port(tmp_path: Path) -> None:
    """Saved facts alone are sufficient for deterministic evaluation."""
    facts_path = tmp_path / "application-facts.json"
    facts_path.write_text(facts_artifact(run_id="saved-run").model_dump_json(), encoding="utf-8")
    result_path = tmp_path / "application-result.json"
    screening = ScreeningWorkflow(
        catalog=program_catalog(),
        facts_extractor=UnusedFactsExtractor(),
        rules_engine=SuccessfulRulesEngine(),
        model_port=None,
        run_id_factory=FixedRunIds("evaluate-operation"),
        config=ScreeningConfig(default_model="gpt-test"),
    )

    outcome = screening.evaluate(
        EvaluateRequest(
            facts_path=facts_path,
            output_path=result_path,
        )
    )

    assert isinstance(outcome, EvaluateCompleted)
    assert outcome.result.run_id == "saved-run"
    assert outcome.result_path == result_path
    assert result_path.read_text(encoding="utf-8").endswith("\n")


def test_screen_evaluates_the_reloaded_saved_artifact(tmp_path: Path) -> None:
    """End-to-end screening crosses the same replay boundary as two commands."""
    original_artifact = facts_artifact(run_id="screen-run")

    class ScreenFactsExtractor:
        """Return the original in-memory artifact for the screen operation."""

        def extract(
            self,
            *,
            run_id: str,
            program: ProgramContext,
            pdf_paths: tuple[Path, ...],
            model_override: str | None,
        ) -> ExtractionSucceeded:
            del pdf_paths, model_override
            assert run_id == "screen-run"
            assert program == original_artifact.program
            return ExtractionSucceeded(kind="EXTRACTION_SUCCEEDED", artifact=original_artifact)

    screening = ScreeningWorkflow(
        catalog=program_catalog(),
        facts_extractor=ScreenFactsExtractor(),
        rules_engine=ReloadRequiredRulesEngine(original_artifact),
        model_port=None,
        run_id_factory=FixedRunIds("screen-run"),
        config=ScreeningConfig(default_model="gpt-test"),
    )

    outcome = screening.screen(
        ScreenRequest(
            program_id="BACHELOR",
            pdf_paths=(tmp_path / "synthetic.pdf",),
            output_dir=tmp_path / "run",
        )
    )

    assert isinstance(outcome, ScreenCompleted)
    assert outcome.artifact == original_artifact
    assert outcome.result.run_id == "screen-run"
    assert outcome.facts_path.name == "application-facts.json"
    assert outcome.result_path.name == "application-result.json"


def test_extract_collision_stops_before_facts_and_preserves_existing_output(tmp_path: Path) -> None:
    """Collision preflight prevents model work and does not clobber user data."""
    output_path = tmp_path / "application-facts.json"
    output_path.write_text("keep me", encoding="utf-8")
    screening = ScreeningWorkflow(
        catalog=program_catalog(),
        facts_extractor=UnusedFactsExtractor(),
        rules_engine=UnusedRulesEngine(),
        model_port=None,
        run_id_factory=FixedRunIds("collision-run"),
        config=ScreeningConfig(default_model="gpt-test"),
    )

    outcome = screening.extract(
        ExtractRequest(
            program_id="BACHELOR",
            pdf_paths=(tmp_path / "synthetic.pdf",),
            output_path=output_path,
        )
    )

    assert isinstance(outcome, RunFailed)
    assert outcome.operation == "EXTRACT"
    assert outcome.failure.stage is FailureStage.OUTPUT_PREFLIGHT
    assert outcome.failure.code == "OUTPUT_EXISTS"
    assert outcome.failure.retryable is False
    assert outcome.failure_path == tmp_path / "processing-failure.json"
    assert output_path.read_text(encoding="utf-8") == "keep me"


class SuccessfulParaphraseModel:
    """Record the presentation-only request and return one strict paraphrase."""

    def __init__(self) -> None:
        self.requests: list[ParaphraseRequest] = []

    def paraphrase_summary(self, request: ParaphraseRequest):  # type: ignore[no-untyped-def]
        self.requests.append(request)
        return ProviderSucceeded[ParaphraseDraft](
            kind="SUCCEEDED",
            output=ParaphraseDraft(text="The application needs manual review under the configured rules."),
            model_returned="gpt-test",
            usage=ProviderUsage(input_tokens=10, output_tokens=12),
            duration_ms=2,
        )


class RefusingParaphraseModel:
    """Return a refusal to prove presentation failure is non-fatal."""

    def paraphrase_summary(self, request: ParaphraseRequest):  # type: ignore[no-untyped-def]
        del request
        return ProviderRefused(kind="REFUSED", duration_ms=1)


def test_evaluate_optional_paraphrase_cannot_change_deterministic_report(tmp_path: Path) -> None:
    """Only the presentation field may differ after the decision is complete."""
    facts_path = tmp_path / "application-facts.json"
    facts_path.write_text(facts_artifact(run_id="saved-run").model_dump_json(), encoding="utf-8")
    model = SuccessfulParaphraseModel()
    screening = ScreeningWorkflow(
        catalog=program_catalog(),
        facts_extractor=UnusedFactsExtractor(),
        rules_engine=SuccessfulRulesEngine(),
        model_port=model,  # type: ignore[arg-type]
        run_id_factory=FixedRunIds("evaluate-operation"),
        config=ScreeningConfig(default_model="gpt-test"),
    )

    outcome = screening.evaluate(
        EvaluateRequest(
            facts_path=facts_path,
            output_path=tmp_path / "application-result.json",
            paraphrase=True,
        )
    )

    assert isinstance(outcome, EvaluateCompleted)
    expected = application_result(run_id="saved-run")
    assert outcome.result.model_copy(update={"summary": expected.summary}) == expected
    assert outcome.result.summary.llm_paraphrase == (
        "The application needs manual review under the configured rules."
    )
    assert model.requests[0].result == expected
    assert model.requests[0].canonical_summary == expected.summary.canonical


def test_evaluate_paraphrase_refusal_keeps_successful_canonical_report(tmp_path: Path) -> None:
    """Optional model failure is a warning and never a processing failure."""
    facts_path = tmp_path / "application-facts.json"
    facts_path.write_text(facts_artifact(run_id="saved-run").model_dump_json(), encoding="utf-8")
    screening = ScreeningWorkflow(
        catalog=program_catalog(),
        facts_extractor=UnusedFactsExtractor(),
        rules_engine=SuccessfulRulesEngine(),
        model_port=RefusingParaphraseModel(),  # type: ignore[arg-type]
        run_id_factory=FixedRunIds("evaluate-operation"),
        config=ScreeningConfig(default_model="gpt-test"),
    )

    outcome = screening.evaluate(
        EvaluateRequest(
            facts_path=facts_path,
            output_path=tmp_path / "application-result.json",
            paraphrase=True,
        )
    )

    assert isinstance(outcome, EvaluateCompleted)
    assert outcome.result == application_result(run_id="saved-run")
    assert "Optional paraphrasing failed; the canonical summary was retained." in outcome.warnings
