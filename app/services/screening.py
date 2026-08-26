"""LangGraph-backed synchronous admissions screening workflow."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.interface import (
    EvaluateCompleted,
    EvaluateRequest,
    ExtractCompleted,
    ExtractRequest,
    ProgressSink,
    RunFailed,
    SafeProgressEvent,
    ScreenCompleted,
    ScreenRequest,
    null_progress,
)
from app.io.artifact_io import (
    ArtifactIOError,
    atomic_write_model,
    load_facts_artifact,
    preflight_output_paths,
)
from app.models.artifacts import ApplicationFactsArtifact
from app.models.failures import FailureStage, ProcessingFailureReport
from app.models.outcomes import (
    EvaluationFailed,
    EvaluationOutcome,
    ExtractionFailed,
    ExtractionOutcome,
)
from app.models.programs import ProgramCatalog, ProgramContext
from app.models.results import ApplicationResult
from app.services.ports import (
    AdmissionsModelPort,
    ParaphraseDraft,
    ParaphraseRequest,
    ProviderSucceeded,
    RunIdFactory,
)


class FactsExtractor(Protocol):
    """Deep facts seam consumed by the screening runtime."""

    def extract(
        self,
        *,
        run_id: str,
        program: ProgramContext,
        pdf_paths: tuple[Path, ...],
        model_override: str | None,
    ) -> ExtractionOutcome:
        """Build one complete persisted-evaluator artifact."""
        ...


class RulesEngine(Protocol):
    """Pure deterministic rules engine seam consumed by the runtime."""

    def evaluate(self, artifact: ApplicationFactsArtifact) -> EvaluationOutcome:
        """Evaluate one complete saved facts artifact."""
        ...


type StageSink = Callable[[str, Mapping[str, object]], None]
"""Debug observer receiving each graph node's name and raw output delta."""


@dataclass(frozen=True)
class ScreeningConfig:
    """Applicant-free configuration needed by private screening graphs."""

    default_model: str
    graph_version: str = "2.0"
    paraphrase_prompt_version: str = "application-result-paraphrase/2.0"
    paraphrase_max_output_tokens: int = 1_000


class _ExtractState(TypedDict, total=False):
    request: ExtractRequest
    run_id: str
    progress: ProgressSink
    program: ProgramContext
    artifact: ApplicationFactsArtifact
    outcome: ExtractCompleted | RunFailed
    failure: ProcessingFailureReport
    warnings: tuple[str, ...]


class _EvaluateState(TypedDict, total=False):
    request: EvaluateRequest
    operation_run_id: str
    progress: ProgressSink
    artifact: ApplicationFactsArtifact
    result: ApplicationResult
    outcome: EvaluateCompleted | RunFailed
    failure: ProcessingFailureReport
    warnings: tuple[str, ...]


class _ScreenState(TypedDict, total=False):
    request: ScreenRequest
    run_id: str
    progress: ProgressSink
    program: ProgramContext
    artifact: ApplicationFactsArtifact
    result: ApplicationResult
    facts_path: Path
    result_path: Path
    outcome: ScreenCompleted | RunFailed
    failure: ProcessingFailureReport
    facts_persisted: bool
    warnings: tuple[str, ...]


class ScreeningWorkflow:
    """Coordinate persistence and deep modules behind the public facade."""

    def __init__(
        self,
        *,
        catalog: ProgramCatalog,
        facts_extractor: FactsExtractor,
        rules_engine: RulesEngine,
        model_port: AdmissionsModelPort | None,
        run_id_factory: RunIdFactory,
        config: ScreeningConfig,
    ) -> None:
        """Initialize the injected screening runtime and compile private graphs."""
        self._catalog = catalog
        self._facts_extractor = facts_extractor
        self._rules_engine = rules_engine
        self._model_port = model_port
        self._run_id_factory = run_id_factory
        self._config = config
        self._extract_graph = self._compile_extract_graph()
        self._evaluate_graph = self._compile_evaluate_graph()
        self._screen_graph = self._compile_screen_graph()

    def extract(
        self,
        request: ExtractRequest,
        *,
        progress: ProgressSink = null_progress,
        stage_sink: StageSink | None = None,
    ) -> ExtractCompleted | RunFailed:
        """Extract, validate, and atomically persist application facts."""
        initial: _ExtractState = {
            "request": request,
            "run_id": self._run_id_factory(),
            "progress": progress,
            "warnings": (),
        }
        result = cast(_ExtractState, self._run_graph(self._extract_graph, initial, stage_sink))
        outcome = result.get("outcome")
        if outcome is None:
            raise RuntimeError("Extract graph completed without an outcome")
        return outcome

    def evaluate(
        self,
        request: EvaluateRequest,
        *,
        progress: ProgressSink = null_progress,
        stage_sink: StageSink | None = None,
    ) -> EvaluateCompleted | RunFailed:
        """Evaluate a saved facts artifact deterministically."""
        initial: _EvaluateState = {
            "request": request,
            "operation_run_id": self._run_id_factory(),
            "progress": progress,
            "warnings": (),
        }
        result = cast(_EvaluateState, self._run_graph(self._evaluate_graph, initial, stage_sink))
        outcome = result.get("outcome")
        if outcome is None:
            raise RuntimeError("Evaluate graph completed without an outcome")
        return outcome

    def screen(
        self,
        request: ScreenRequest,
        *,
        progress: ProgressSink = null_progress,
        stage_sink: StageSink | None = None,
    ) -> ScreenCompleted | RunFailed:
        """Extract and evaluate through the exact serialized facts artifact."""
        initial: _ScreenState = {
            "request": request,
            "run_id": self._run_id_factory(),
            "progress": progress,
            "facts_path": request.output_dir / "application-facts.json",
            "result_path": request.output_dir / "application-result.json",
            "warnings": (),
        }
        result = cast(_ScreenState, self._run_graph(self._screen_graph, initial, stage_sink))
        outcome = result.get("outcome")
        if outcome is None:
            raise RuntimeError("Screen graph completed without an outcome")
        return outcome

    def _run_graph(
        self,
        graph: CompiledStateGraph[Any, None, Any, Any],
        initial: Mapping[str, Any],
        stage_sink: StageSink | None,
    ) -> dict[str, Any]:
        """Stream one compiled graph to completion, exposing each node's output delta."""
        state: dict[str, Any] = dict(initial)
        for chunk in graph.stream(initial, stream_mode="updates"):
            for node_name, delta in chunk.items():
                if not isinstance(delta, dict):
                    continue
                state.update(delta)
                if stage_sink is not None:
                    try:
                        stage_sink(node_name, delta)
                    except Exception:
                        stage_sink = None
        return state

    def _compile_extract_graph(
        self,
    ) -> CompiledStateGraph[_ExtractState, None, _ExtractState, _ExtractState]:
        builder = StateGraph(_ExtractState)
        builder.add_node("preflight_outputs", self._extract_preflight)
        builder.add_node("resolve_program", self._extract_resolve_program)
        builder.add_node("build_facts", self._extract_build_facts)
        builder.add_node("write_facts", self._extract_write_facts)
        builder.add_node("finalize_failure", self._extract_finalize_failure)
        builder.add_edge(START, "preflight_outputs")
        builder.add_conditional_edges(
            "preflight_outputs",
            self._route_on_failure,
            {"continue": "resolve_program", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "resolve_program",
            self._route_on_failure,
            {"continue": "build_facts", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "build_facts",
            self._route_on_failure,
            {"continue": "write_facts", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "write_facts",
            self._route_on_completion,
            {"complete": END, "failed": "finalize_failure"},
        )
        builder.add_edge("finalize_failure", END)
        return builder.compile()

    def _compile_evaluate_graph(
        self,
    ) -> CompiledStateGraph[_EvaluateState, None, _EvaluateState, _EvaluateState]:
        builder = StateGraph(_EvaluateState)
        builder.add_node("preflight_outputs", self._evaluate_preflight)
        builder.add_node("load_facts", self._evaluate_load_facts)
        builder.add_node("evaluate_policy", self._evaluate_policy)
        builder.add_node("optional_paraphrase", self._evaluate_optional_paraphrase)
        builder.add_node("write_report", self._evaluate_write_report)
        builder.add_node("finalize_failure", self._evaluate_finalize_failure)
        builder.add_edge(START, "preflight_outputs")
        builder.add_conditional_edges(
            "preflight_outputs",
            self._route_on_failure,
            {"continue": "load_facts", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "load_facts",
            self._route_on_failure,
            {"continue": "evaluate_policy", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "evaluate_policy",
            self._route_on_failure,
            {"continue": "optional_paraphrase", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "optional_paraphrase",
            self._route_on_failure,
            {"continue": "write_report", "failed": "finalize_failure"},
        )
        builder.add_conditional_edges(
            "write_report",
            self._route_on_completion,
            {"complete": END, "failed": "finalize_failure"},
        )
        builder.add_edge("finalize_failure", END)
        return builder.compile()

    def _compile_screen_graph(
        self,
    ) -> CompiledStateGraph[_ScreenState, None, _ScreenState, _ScreenState]:
        builder = StateGraph(_ScreenState)
        builder.add_node("preflight_outputs", self._screen_preflight)
        builder.add_node("resolve_program", self._screen_resolve_program)
        builder.add_node("build_facts", self._screen_build_facts)
        builder.add_node("write_facts", self._screen_write_facts)
        builder.add_node("reload_facts", self._screen_reload_facts)
        builder.add_node("evaluate_policy", self._screen_evaluate_policy)
        builder.add_node("optional_paraphrase", self._screen_optional_paraphrase)
        builder.add_node("write_report", self._screen_write_report)
        builder.add_node("finalize_failure", self._screen_finalize_failure)
        builder.add_edge(START, "preflight_outputs")
        for source, destination in (
            ("preflight_outputs", "resolve_program"),
            ("resolve_program", "build_facts"),
            ("build_facts", "write_facts"),
            ("write_facts", "reload_facts"),
            ("reload_facts", "evaluate_policy"),
            ("evaluate_policy", "optional_paraphrase"),
            ("optional_paraphrase", "write_report"),
        ):
            builder.add_conditional_edges(
                source,
                self._route_on_failure,
                {"continue": destination, "failed": "finalize_failure"},
            )
        builder.add_conditional_edges(
            "write_report",
            self._route_on_completion,
            {"complete": END, "failed": "finalize_failure"},
        )
        builder.add_edge("finalize_failure", END)
        return builder.compile()

    def _extract_preflight(self, state: _ExtractState) -> _ExtractState:
        request = state["request"]
        try:
            preflight_output_paths(
                (request.output_path, request.output_path.parent / "processing-failure.json"),
                overwrite=request.overwrite,
            )
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["run_id"], FailureStage.OUTPUT_PREFLIGHT, exc)}
        return {"warnings": self._progress(state, "output_preflight", "Output paths are ready.")}

    def _extract_resolve_program(self, state: _ExtractState) -> _ExtractState:
        try:
            program = self._catalog.resolve(state["request"].program_id)
        except ValueError:
            return {
                "failure": ProcessingFailureReport(
                    kind="PROCESSING_FAILURE",
                    report_version="1.0",
                    run_id=state["run_id"],
                    stage=FailureStage.PROGRAM_RESOLUTION,
                    code="PROGRAM_NOT_CONFIGURED",
                    safe_message="The selected study program is not configured.",
                    retryable=False,
                )
            }
        return {
            "program": program,
            "warnings": self._progress(state, "program_resolution", "Program configuration is resolved."),
        }

    def _extract_build_facts(self, state: _ExtractState) -> _ExtractState:
        request = state["request"]
        outcome = self._facts_extractor.extract(
            run_id=state["run_id"],
            program=state["program"],
            pdf_paths=request.pdf_paths,
            model_override=request.model or self._config.default_model,
        )
        if isinstance(outcome, ExtractionFailed):
            if outcome.failure.run_id != state["run_id"]:
                raise RuntimeError("Facts extractor returned a failure for a different application")
            return {
                "failure": outcome.failure,
                "warnings": (*state.get("warnings", ()), *outcome.warnings),
            }
        if outcome.artifact.run_id != state["run_id"] or outcome.artifact.program != state["program"]:
            raise RuntimeError("Facts extractor returned an artifact for a different application")
        return {
            "artifact": outcome.artifact,
            "warnings": (*state.get("warnings", ()), *outcome.warnings),
        }

    def _extract_write_facts(self, state: _ExtractState) -> _ExtractState:
        request = state["request"]
        artifact = state["artifact"]
        try:
            atomic_write_model(request.output_path, artifact, overwrite=request.overwrite)
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["run_id"], FailureStage.ARTIFACT_WRITE, exc)}
        warnings = self._progress(state, "artifact_write", "Application facts are saved.")
        outcome = ExtractCompleted(
            kind="EXTRACT_COMPLETED",
            artifact=artifact,
            facts_path=request.output_path,
            warnings=warnings,
        )
        return {"outcome": outcome, "warnings": outcome.warnings}

    def _extract_finalize_failure(self, state: _ExtractState) -> _ExtractState:
        request = state["request"]
        outcome = self._failed_outcome(
            operation="EXTRACT",
            failure=state["failure"],
            failure_path=request.output_path.parent / "processing-failure.json",
            retained_facts_path=None,
            overwrite=request.overwrite,
            warnings=state.get("warnings", ()),
        )
        return {"outcome": outcome, "warnings": outcome.warnings}

    def _evaluate_preflight(self, state: _EvaluateState) -> _EvaluateState:
        request = state["request"]
        if request.facts_path in (request.output_path, request.output_path.parent / "processing-failure.json"):
            return {
                "failure": ProcessingFailureReport(
                    kind="PROCESSING_FAILURE",
                    report_version="1.0",
                    run_id=state["operation_run_id"],
                    stage=FailureStage.OUTPUT_PREFLIGHT,
                    code="OUTPUT_OVERLAPS_INPUT",
                    safe_message="An output path overlaps the saved facts input.",
                    retryable=False,
                )
            }
        try:
            preflight_output_paths(
                (request.output_path, request.output_path.parent / "processing-failure.json"),
                overwrite=request.overwrite,
            )
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["operation_run_id"], FailureStage.OUTPUT_PREFLIGHT, exc)}
        return {"warnings": self._evaluate_progress(state, "output_preflight", "Output paths are ready.")}

    def _evaluate_load_facts(self, state: _EvaluateState) -> _EvaluateState:
        try:
            artifact = load_facts_artifact(state["request"].facts_path)
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["operation_run_id"], FailureStage.ARTIFACT_LOAD, exc)}
        return {
            "artifact": artifact,
            "warnings": self._evaluate_progress(state, "artifact_load", "Saved application facts are loaded."),
        }

    def _evaluate_policy(self, state: _EvaluateState) -> _EvaluateState:
        outcome = self._rules_engine.evaluate(state["artifact"])
        if isinstance(outcome, EvaluationFailed):
            if outcome.failure.run_id != state["artifact"].run_id:
                raise RuntimeError("Rules engine returned a failure for a different application")
            return {"failure": outcome.failure}
        if outcome.result.run_id != state["artifact"].run_id:
            raise RuntimeError("Rules engine returned a result for a different application")
        return {
            "result": outcome.result,
            "warnings": self._evaluate_progress(state, "evaluation", "Deterministic evaluation is complete."),
        }

    def _evaluate_optional_paraphrase(self, state: _EvaluateState) -> _EvaluateState:
        result, warnings = self._optional_paraphrase(
            result=state["result"],
            enabled=state["request"].paraphrase,
            warnings=state.get("warnings", ()),
        )
        if result is state["result"]:
            return {"warnings": warnings}
        return {"result": result, "warnings": warnings}

    def _evaluate_write_report(self, state: _EvaluateState) -> _EvaluateState:
        request = state["request"]
        result = state["result"]
        try:
            atomic_write_model(request.output_path, result, overwrite=request.overwrite)
        except ArtifactIOError as exc:
            return {"failure": self._failure(result.run_id, FailureStage.ARTIFACT_WRITE, exc)}
        warnings = self._evaluate_progress(state, "artifact_write", "Application result is saved.")
        outcome = EvaluateCompleted(
            kind="EVALUATE_COMPLETED",
            result=result,
            result_path=request.output_path,
            warnings=warnings,
        )
        return {"outcome": outcome, "warnings": outcome.warnings}

    def _evaluate_finalize_failure(self, state: _EvaluateState) -> _EvaluateState:
        request = state["request"]
        outcome = self._failed_outcome(
            operation="EVALUATE",
            failure=state["failure"],
            failure_path=request.output_path.parent / "processing-failure.json",
            retained_facts_path=None,
            overwrite=request.overwrite,
            warnings=state.get("warnings", ()),
        )
        return {"outcome": outcome, "warnings": outcome.warnings}

    def _screen_preflight(self, state: _ScreenState) -> _ScreenState:
        request = state["request"]
        try:
            preflight_output_paths(
                (
                    state["facts_path"],
                    state["result_path"],
                    request.output_dir / "processing-failure.json",
                ),
                overwrite=request.overwrite,
            )
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["run_id"], FailureStage.OUTPUT_PREFLIGHT, exc)}
        return {"warnings": self._screen_progress(state, "output_preflight", "Output paths are ready.")}

    def _screen_resolve_program(self, state: _ScreenState) -> _ScreenState:
        try:
            program = self._catalog.resolve(state["request"].program_id)
        except ValueError:
            return {
                "failure": ProcessingFailureReport(
                    kind="PROCESSING_FAILURE",
                    report_version="1.0",
                    run_id=state["run_id"],
                    stage=FailureStage.PROGRAM_RESOLUTION,
                    code="PROGRAM_NOT_CONFIGURED",
                    safe_message="The selected study program is not configured.",
                    retryable=False,
                )
            }
        return {
            "program": program,
            "warnings": self._screen_progress(state, "program_resolution", "Program configuration is resolved."),
        }

    def _screen_build_facts(self, state: _ScreenState) -> _ScreenState:
        request = state["request"]
        outcome = self._facts_extractor.extract(
            run_id=state["run_id"],
            program=state["program"],
            pdf_paths=request.pdf_paths,
            model_override=request.model or self._config.default_model,
        )
        if isinstance(outcome, ExtractionFailed):
            if outcome.failure.run_id != state["run_id"]:
                raise RuntimeError("Facts extractor returned a failure for a different application")
            return {
                "failure": outcome.failure,
                "warnings": (*state.get("warnings", ()), *outcome.warnings),
            }
        if outcome.artifact.run_id != state["run_id"] or outcome.artifact.program != state["program"]:
            raise RuntimeError("Facts extractor returned an artifact for a different application")
        return {
            "artifact": outcome.artifact,
            "warnings": (*state.get("warnings", ()), *outcome.warnings),
        }

    def _screen_write_facts(self, state: _ScreenState) -> _ScreenState:
        try:
            atomic_write_model(state["facts_path"], state["artifact"], overwrite=state["request"].overwrite)
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["run_id"], FailureStage.ARTIFACT_WRITE, exc)}
        return {
            "facts_persisted": True,
            "warnings": self._screen_progress(state, "artifact_write", "Application facts are saved."),
        }

    def _screen_reload_facts(self, state: _ScreenState) -> _ScreenState:
        try:
            artifact = load_facts_artifact(state["facts_path"])
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["run_id"], FailureStage.ARTIFACT_LOAD, exc)}
        return {
            "artifact": artifact,
            "warnings": self._screen_progress(state, "artifact_load", "Saved application facts are reloaded."),
        }

    def _screen_evaluate_policy(self, state: _ScreenState) -> _ScreenState:
        outcome = self._rules_engine.evaluate(state["artifact"])
        if isinstance(outcome, EvaluationFailed):
            if outcome.failure.run_id != state["artifact"].run_id:
                raise RuntimeError("Rules engine returned a failure for a different application")
            return {"failure": outcome.failure}
        if outcome.result.run_id != state["artifact"].run_id:
            raise RuntimeError("Rules engine returned a result for a different application")
        return {
            "result": outcome.result,
            "warnings": self._screen_progress(state, "evaluation", "Deterministic evaluation is complete."),
        }

    def _screen_optional_paraphrase(self, state: _ScreenState) -> _ScreenState:
        result, warnings = self._optional_paraphrase(
            result=state["result"],
            enabled=state["request"].paraphrase,
            warnings=state.get("warnings", ()),
        )
        if result is state["result"]:
            return {"warnings": warnings}
        return {"result": result, "warnings": warnings}

    def _screen_write_report(self, state: _ScreenState) -> _ScreenState:
        try:
            atomic_write_model(state["result_path"], state["result"], overwrite=state["request"].overwrite)
        except ArtifactIOError as exc:
            return {"failure": self._failure(state["result"].run_id, FailureStage.ARTIFACT_WRITE, exc)}
        warnings = self._screen_progress(state, "artifact_write", "Application result is saved.")
        outcome = ScreenCompleted(
            kind="SCREEN_COMPLETED",
            artifact=state["artifact"],
            result=state["result"],
            facts_path=state["facts_path"],
            result_path=state["result_path"],
            warnings=warnings,
        )
        return {"outcome": outcome, "warnings": outcome.warnings}

    def _screen_finalize_failure(self, state: _ScreenState) -> _ScreenState:
        request = state["request"]
        retained_path = state["facts_path"] if state.get("facts_persisted", False) else None
        outcome = self._failed_outcome(
            operation="SCREEN",
            failure=state["failure"],
            failure_path=request.output_dir / "processing-failure.json",
            retained_facts_path=retained_path,
            overwrite=request.overwrite,
            warnings=state.get("warnings", ()),
        )
        return {"outcome": outcome, "warnings": outcome.warnings}

    def _progress(self, state: _ExtractState, stage: str, message: str) -> tuple[str, ...]:
        warnings = state.get("warnings", ())
        try:
            state["progress"](SafeProgressEvent(stage=stage, message=message))
        except Exception:
            return (*warnings, "Progress reporting failed; processing continued.")
        return warnings

    def _evaluate_progress(self, state: _EvaluateState, stage: str, message: str) -> tuple[str, ...]:
        warnings = state.get("warnings", ())
        try:
            state["progress"](SafeProgressEvent(stage=stage, message=message))
        except Exception:
            return (*warnings, "Progress reporting failed; processing continued.")
        return warnings

    def _screen_progress(self, state: _ScreenState, stage: str, message: str) -> tuple[str, ...]:
        warnings = state.get("warnings", ())
        try:
            state["progress"](SafeProgressEvent(stage=stage, message=message))
        except Exception:
            return (*warnings, "Progress reporting failed; processing continued.")
        return warnings

    def _optional_paraphrase(
        self,
        *,
        result: ApplicationResult,
        enabled: bool,
        warnings: tuple[str, ...],
    ) -> tuple[ApplicationResult, tuple[str, ...]]:
        if not enabled:
            return result, warnings
        if self._model_port is None:
            return result, (*warnings, "Optional paraphrasing was unavailable; the canonical summary was retained.")

        paraphrase = self._model_port.paraphrase_summary(
            ParaphraseRequest(
                result=result,
                canonical_summary=result.summary.canonical,
                model=self._config.default_model,
                prompt_version=self._config.paraphrase_prompt_version,
                max_output_tokens=self._config.paraphrase_max_output_tokens,
            )
        )
        if not isinstance(paraphrase, ProviderSucceeded) or not isinstance(paraphrase.output, ParaphraseDraft):
            return result, (*warnings, "Optional paraphrasing failed; the canonical summary was retained.")

        summary = result.summary.model_copy(update={"llm_paraphrase": paraphrase.output.text})
        return result.model_copy(update={"summary": summary}), warnings

    @staticmethod
    def _route_on_failure(
        state: _ExtractState | _EvaluateState | _ScreenState,
    ) -> Literal["continue", "failed"]:
        return "failed" if "failure" in state else "continue"

    @staticmethod
    def _route_on_completion(
        state: _ExtractState | _EvaluateState | _ScreenState,
    ) -> Literal["complete", "failed"]:
        return "failed" if "failure" in state else "complete"

    @staticmethod
    def _failure(run_id: str, stage: FailureStage, error: ArtifactIOError) -> ProcessingFailureReport:
        return ProcessingFailureReport(
            kind="PROCESSING_FAILURE",
            report_version="1.0",
            run_id=run_id,
            stage=stage,
            code=error.code,
            safe_message=error.safe_message,
            retryable=False,
        )

    def _failed_outcome(
        self,
        *,
        operation: Literal["EXTRACT", "EVALUATE", "SCREEN"],
        failure: ProcessingFailureReport,
        failure_path: Path,
        retained_facts_path: Path | None,
        overwrite: bool,
        warnings: tuple[str, ...],
    ) -> RunFailed:
        written_failure_path: Path | None = None
        final_warnings = warnings
        try:
            atomic_write_model(failure_path, failure, overwrite=overwrite)
            written_failure_path = failure_path
        except ArtifactIOError:
            final_warnings = (*final_warnings, "The processing-failure artifact could not be written.")

        return RunFailed(
            kind="RUN_FAILED",
            operation=operation,
            failure=failure,
            failure_path=written_failure_path,
            retained_facts_path=retained_facts_path,
            warnings=final_warnings,
        )
