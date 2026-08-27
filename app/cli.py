"""Typer command-line interface for local admissions screening."""

import json
from collections.abc import Mapping
from itertools import count
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from pydantic import BaseModel, ValidationError

from app.bootstrap import AdmissionsSettings, BootstrapError, build_screening
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
from app.models.failures import FailureStage
from app.models.results import ApplicationResult
from app.services.screening import ScreeningWorkflow, StageSink

app = typer.Typer(
    name="auto-admissions",
    help="Assess candidates credentials against the rules",
    no_args_is_help=True,
)


def _build(*, trace: bool, require_openai: bool, rules_root: Path | None = None) -> ScreeningWorkflow:
    overrides: dict[str, Path] = {}
    if rules_root is not None:
        overrides["rules_root"] = rules_root
        # A generated package ships the catalog pinning its own policy version, so take
        # that one: the default catalog pins a different version and fails activation.
        packaged_catalog = rules_root / "programs.yaml"
        if packaged_catalog.is_file():
            overrides["catalog_path"] = packaged_catalog
    try:
        settings = AdmissionsSettings(trace_enabled=trace, **overrides)
    except ValidationError:
        typer.echo("Configuration is invalid.", err=True)
        raise typer.Exit(2) from None
    if require_openai and settings.openai_key_value is None:
        typer.echo("OPENAI_API_KEY is required for this operation.", err=True)
        raise typer.Exit(2)
    try:
        return build_screening(settings)
    except BootstrapError as error:
        typer.echo(f"{error.code}: {error.safe_message}", err=True)
        raise typer.Exit(error.exit_code) from None


def _progress_sink(quiet: bool) -> ProgressSink:
    if quiet:
        return null_progress

    def emit(event: SafeProgressEvent) -> None:
        typer.echo(f"[{event.stage}] {event.message}", err=True)

    return emit


def _stage_sink(directory: Path | None) -> StageSink | None:
    if directory is None:
        return None
    numbers = count(1)

    def write(node: str, delta: Mapping[str, object]) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        payload = {
            key: value.model_dump(mode="json") if isinstance(value, BaseModel) else value
            for key, value in delta.items()
        }
        path = directory / f"{next(numbers):02d}-{node}.json"
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        typer.echo(f"[stage] {node} -> {path}", err=True)

    return write


def _print_summary(result: ApplicationResult) -> None:
    typer.echo(result.summary.canonical.headline)
    typer.echo(result.summary.llm_paraphrase or result.summary.canonical.explanation)
    for item in result.summary.canonical.required_information:
        typer.echo(f"Required: {item}")


def _fail(outcome: RunFailed) -> NoReturn:
    typer.echo(f"{outcome.failure.code}: {outcome.failure.safe_message}", err=True)
    if outcome.failure_path is not None:
        typer.echo(f"Failure saved: {outcome.failure_path}", err=True)
    raise typer.Exit(_failure_exit_code(outcome.failure.stage))


def _failure_exit_code(stage: FailureStage) -> int:
    if stage in {FailureStage.CONFIGURATION, FailureStage.PROGRAM_RESOLUTION}:
        return 2
    if stage is FailureStage.PDF_INGESTION:
        return 3
    if stage in {FailureStage.OUTPUT_PREFLIGHT, FailureStage.ARTIFACT_WRITE}:
        return 4
    if stage in {FailureStage.EXTRACTION, FailureStage.FACTS_VALIDATION}:
        return 5
    return 6


@app.command()
def extract(
    pdfs: Annotated[
        list[Path],
        typer.Argument(help="One or more applicant PDF files.", exists=True, file_okay=True, dir_okay=False),
    ],
    program: Annotated[str, typer.Option("--program", help="Configured program ID.")],
    output: Annotated[Path, typer.Option("--output", help="ApplicationFacts artifact path.")],
    model: Annotated[str | None, typer.Option("--model", help="OpenAI model override.")] = None,
    trace: Annotated[bool, typer.Option("--trace", help="Enable full LangSmith tracing.")] = False,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Overwrite output artifacts")] = True,
    quiet: Annotated[bool, typer.Option("--quiet", help="Suppress safe progress messages.")] = False,
    stages: Annotated[bool, typer.Option("--stages", help="Write each pipeline stage's output to a stages/ folder.")] = False,
) -> None:
    """Extract strict final application facts from a complete PDF bundle."""
    screening = _build(trace=trace, require_openai=True)
    outcome = screening.extract(
        ExtractRequest(
            program_id=program,
            pdf_paths=tuple(pdfs),
            output_path=output,
            model=model,
            overwrite=overwrite,
        ),
        progress=_progress_sink(quiet),
        stage_sink=_stage_sink(output.parent / "stages" if stages else None),
    )
    if isinstance(outcome, RunFailed):
        _fail(outcome)
    if not isinstance(outcome, ExtractCompleted):
        raise RuntimeError("Extract returned an unsupported outcome")
    typer.echo(f"Application facts saved: {outcome.facts_path}")


@app.command()
def evaluate(
    facts: Annotated[
        Path,
        typer.Option("--facts", help="Saved ApplicationFacts artifact.", exists=True, file_okay=True, dir_okay=False),
    ],
    output: Annotated[Path, typer.Option("--output", help="Application result path.")],
    paraphrase: Annotated[
        bool,
        typer.Option("--paraphrase", help="Add an optional post-decision OpenAI paraphrase."),
    ] = False,
    trace: Annotated[bool, typer.Option("--trace", help="Enable full LangSmith tracing.")] = False,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Replace exact command-owned outputs.")] = True,
    quiet: Annotated[bool, typer.Option("--quiet", help="Suppress safe progress messages.")] = False,
    stages: Annotated[bool, typer.Option("--stages", help="Write each pipeline stage's output to a stages/ folder.")] = False,
) -> None:
    """Evaluate a saved facts artifact without OpenAI unless paraphrasing."""
    screening = _build(trace=trace, require_openai=paraphrase)
    outcome = screening.evaluate(
        EvaluateRequest(
            facts_path=facts,
            output_path=output,
            paraphrase=paraphrase,
            overwrite=overwrite,
        ),
        progress=_progress_sink(quiet),
        stage_sink=_stage_sink(output.parent / "stages" if stages else None),
    )
    if isinstance(outcome, RunFailed):
        _fail(outcome)
    if not isinstance(outcome, EvaluateCompleted):
        raise RuntimeError("Evaluate returned an unsupported outcome")
    _print_summary(outcome.result)
    typer.echo(f"Result saved: {outcome.result_path}")


@app.command()
def screen(
    pdfs: Annotated[
        list[Path],
        typer.Argument(help="One or more applicant PDF files.", exists=True, file_okay=True, dir_okay=False),
    ],
    program: Annotated[str, typer.Option("--program", help="Configured program ID.")],
    output_dir: Annotated[Path, typer.Option("--output-dir", help="Directory for both JSON outputs.")],
    model: Annotated[str | None, typer.Option("--model", help="OpenAI model override.")] = None,
    paraphrase: Annotated[
        bool,
        typer.Option("--paraphrase", help="Add an optional post-decision OpenAI paraphrase."),
    ] = False,
    trace: Annotated[bool, typer.Option("--trace", help="Enable full LangSmith tracing.")] = False,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Replace exact command-owned outputs.")] = True,
    quiet: Annotated[bool, typer.Option("--quiet", help="Suppress safe progress messages.")] = False,
    stages: Annotated[bool, typer.Option("--stages", help="Write each pipeline stage's output to a stages/ folder.")] = False,
    rules_root: Annotated[
        Path | None,
        typer.Option(
            "--rules-root",
            help="Rules package to activate instead of rules/. Use to screen against a candidate package.",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """Run extraction and deterministic evaluation through the saved artifact."""
    screening = _build(trace=trace, require_openai=True, rules_root=rules_root)
    # One folder per applicant, taken from the bundle directory the PDFs came from, so
    # screening several people into one --output-dir does not overwrite the last result.
    # Derived here rather than in the request: the screening service stays applicant-free.
    applicant_dir = output_dir / (pdfs[0].parent.name or pdfs[0].stem)
    outcome = screening.screen(
        ScreenRequest(
            program_id=program,
            pdf_paths=tuple(pdfs),
            output_dir=applicant_dir,
            model=model,
            paraphrase=paraphrase,
            overwrite=overwrite,
        ),
        progress=_progress_sink(quiet),
        stage_sink=_stage_sink(applicant_dir / "stages" if stages else None),
    )
    if isinstance(outcome, RunFailed):
        _fail(outcome)
    if not isinstance(outcome, ScreenCompleted):
        raise RuntimeError("Screen returned an unsupported outcome")
    _print_summary(outcome.result)
    typer.echo(f"Facts saved: {outcome.facts_path}")
    typer.echo(f"Result saved: {outcome.result_path}")
