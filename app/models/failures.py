"""Typed processing failures kept separate from applicant outcomes."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    """Base configuration for immutable, strict failure contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class FailureStage(StrEnum):
    """Stable workflow stages that can end before a decision is produced."""

    CONFIGURATION = "CONFIGURATION"
    OUTPUT_PREFLIGHT = "OUTPUT_PREFLIGHT"
    PROGRAM_RESOLUTION = "PROGRAM_RESOLUTION"
    PDF_INGESTION = "PDF_INGESTION"
    EXTRACTION = "EXTRACTION"
    FACTS_VALIDATION = "FACTS_VALIDATION"
    ARTIFACT_LOAD = "ARTIFACT_LOAD"
    POLICY_ACTIVATION = "POLICY_ACTIVATION"
    EVALUATION = "EVALUATION"
    REPORT_COMPOSITION = "REPORT_COMPOSITION"
    ARTIFACT_WRITE = "ARTIFACT_WRITE"


class ProcessingFailureReport(ContractModel):
    """Safe local description of a workflow failure without eligibility data."""

    kind: Literal["PROCESSING_FAILURE"]
    report_version: Literal["1.0"]
    run_id: str
    stage: FailureStage
    code: str
    safe_message: str
    retryable: bool
