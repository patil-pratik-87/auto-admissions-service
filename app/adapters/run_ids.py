"""Local operation identifier adapters."""

from uuid import uuid4


class UuidRunIds:
    """Create opaque local operation identifiers."""

    def __call__(self) -> str:
        """Return a fresh identifier without applicant content."""
        return f"run-{uuid4()}"
