import pytest
from pydantic import ValidationError

from app.models.documents import DocumentManifest


def test_manifest_rejects_totals_that_do_not_describe_its_documents() -> None:
    """Manifest summary values must be derived from the trusted entries."""
    with pytest.raises(ValidationError, match="total_bytes"):
        DocumentManifest.model_validate(
            {
                "manifest_version": "1.0",
                "documents": [
                    {
                        "document_id": "sha256:" + "a" * 64,
                        "original_filename": "certificate.pdf",
                        "sha256": "a" * 64,
                        "byte_size": 100,
                        "page_count": 2,
                        "duplicate_filenames": [],
                    }
                ],
                "total_bytes": 99,
                "total_pages": 2,
            }
        )
