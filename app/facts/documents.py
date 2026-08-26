"""Private PDF preflight seam used by the facts extractor."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.models.documents import DocumentManifestEntry


class PdfRejected(Exception):
    """Safe rejection reason translated into an ingestion failure."""

    def __init__(self, code: str, safe_message: str) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message


@dataclass(frozen=True, slots=True)
class AcceptedDocument:
    """One unique PDF and the exact bytes accepted during preflight."""

    path: Path
    content: bytes
    manifest_entry: DocumentManifestEntry


class PdfPreflight(Protocol):
    """Local seam that accepts one readable PDF and reports its page count."""

    def accept(self, content: bytes) -> int:
        """Validate and render every page, returning the page count."""
        ...

