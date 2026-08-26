"""Trusted PDF document manifest contracts."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


class ContractModel(BaseModel):
    """Base configuration for immutable, strict document contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


Sha256Digest = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class DocumentManifestEntry(ContractModel):
    """Content-addressed identity and safe metadata for one unique PDF."""

    document_id: str
    original_filename: str = Field(min_length=1)
    sha256: Sha256Digest
    byte_size: int = Field(gt=0)
    page_count: int = Field(ge=1)
    duplicate_filenames: tuple[str, ...] = ()

    @model_validator(mode="after")
    def document_id_matches_digest(self) -> Self:
        """Bind every document identifier to the exact accepted bytes."""
        if self.document_id != f"sha256:{self.sha256}":
            raise ValueError("document_id must match sha256")
        return self


class DocumentManifest(ContractModel):
    """Complete deterministic description of an accepted PDF bundle."""

    manifest_version: Literal["1.0"]
    documents: tuple[DocumentManifestEntry, ...] = Field(min_length=1)
    total_bytes: int = Field(gt=0)
    total_pages: int = Field(ge=1)

    @model_validator(mode="after")
    def summaries_and_order_are_canonical(self) -> Self:
        """Require trustworthy totals, unique identities, and stable ordering."""
        if self.total_bytes != sum(document.byte_size for document in self.documents):
            raise ValueError("total_bytes does not match document entries")
        if self.total_pages != sum(document.page_count for document in self.documents):
            raise ValueError("total_pages does not match document entries")

        document_ids = tuple(document.document_id for document in self.documents)
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("document identifiers must be unique")
        if document_ids != tuple(sorted(document_ids)):
            raise ValueError("documents must be sorted by document_id")
        return self
