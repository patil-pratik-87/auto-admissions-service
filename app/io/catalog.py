"""Strict loading of the trusted configured program catalog."""

from pathlib import Path

from pydantic import ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from app.models.programs import ProgramCatalog


class CatalogError(Exception):
    """Expected catalog load error with a stable public code."""

    def __init__(self, code: str, safe_message: str) -> None:
        """Initialize a safe catalog error."""
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message


def load_program_catalog(path: Path) -> ProgramCatalog:
    """Load and validate the trusted configured program catalog.

    Args:
        path: Filesystem path to the configured catalog document.

    Returns:
        The validated immutable program catalog.

    Raises:
        CatalogError: If the catalog is missing, unreadable, or invalid.
    """
    yaml = YAML(typ="safe")
    yaml.allow_duplicate_keys = False
    try:
        with path.open("r", encoding="utf-8") as stream:
            payload = yaml.load(stream)
        return ProgramCatalog.model_validate(payload)
    except FileNotFoundError as error:
        raise CatalogError("CATALOG_NOT_FOUND", "The configured program catalog was not found.") from error
    except (OSError, YAMLError, ValidationError, ValueError) as error:
        raise CatalogError("CATALOG_INVALID", "The configured program catalog is invalid.") from error
