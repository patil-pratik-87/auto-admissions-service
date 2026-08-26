"""Versioned facts artifact used for deterministic replay."""

from collections.abc import Iterator
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.documents import DocumentManifest
from app.models.facts import ApplicationFacts, EvidenceRef
from app.models.programs import ProgramContext


class ContractModel(BaseModel):
    """Base configuration for immutable, strict artifact contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class FactsArtifactVersions(ContractModel):
    """Versions needed to understand how direct facts were produced."""

    extraction_prompt: str
    model_requested: str
    model_returned: str


class ProviderAttemptMetadata(ContractModel):
    """Local technical metadata for one bounded provider attempt."""

    operation: Literal["EXTRACTION", "PARAPHRASE"]
    attempt_number: int = Field(ge=1, le=2)
    model_requested: str
    model_returned: str | None = None
    response_status: str
    request_id: str | None = None
    error_category: str | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    duration_ms: int = Field(ge=0)


def _iter_evidence(value: object) -> Iterator[EvidenceRef]:
    """Walk one validated facts tree without depending on concrete fact types."""
    if isinstance(value, EvidenceRef):
        yield value
        return
    if isinstance(value, BaseModel):
        for field_name in type(value).model_fields:
            yield from _iter_evidence(getattr(value, field_name))
        return
    if isinstance(value, tuple):
        for item in value:
            yield from _iter_evidence(item)


class ApplicationFactsArtifact(ContractModel):
    """Complete saved input consumed by deterministic evaluation."""

    kind: Literal["APPLICATION_FACTS"]
    artifact_version: Literal["2.0"]
    run_id: str
    program: ProgramContext
    manifest: DocumentManifest
    facts: ApplicationFacts
    versions: FactsArtifactVersions
    attempts: tuple[ProviderAttemptMetadata, ...] = ()
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def evidence_references_stay_inside_manifest(self) -> "ApplicationFactsArtifact":
        """Validate pointer identity and bounds without asserting factual support."""
        pages_by_document = {
            document.document_id: document.page_count for document in self.manifest.documents
        }
        for reference in _iter_evidence(self.facts):
            page_count = pages_by_document.get(reference.document_id)
            if page_count is None:
                raise ValueError("evidence references an unknown document")
            if reference.page_number > page_count:
                raise ValueError("evidence page is outside the document")
        return self
