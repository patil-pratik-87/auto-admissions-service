from pathlib import Path

import pytest
from pydantic import ValidationError

from app import ExtractRequest


def test_extract_request_requires_at_least_one_pdf() -> None:
    """Extraction cannot turn an empty bundle into empty application facts."""
    with pytest.raises(ValidationError):
        ExtractRequest(
            program_id="BACHELOR",
            pdf_paths=(),
            output_path=Path("application-facts.json"),
        )
