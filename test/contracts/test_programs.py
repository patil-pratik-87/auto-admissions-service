from pathlib import Path

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML

from app.models.programs import ProgramCatalog


def test_catalog_resolves_the_trusted_bachelor_context() -> None:
    """The configured selection resolves values documents cannot override."""
    catalog_path = Path(__file__).parents[2] / "config" / "programs.yaml"
    payload = YAML(typ="safe").load(catalog_path)

    catalog = ProgramCatalog.model_validate(payload)
    context = catalog.resolve("BACHELOR")

    assert context.program_id == "BACHELOR"
    assert context.display_name == "Bachelor's Study Program"
    assert context.study_level == "BACHELOR"
    assert context.program_subject == "COMPUTER_SCIENCE"
    assert context.policy.id == "IU_BACHELOR_ACCESS"
    assert context.policy.version == "0.0.22"


def test_catalog_rejects_duplicate_program_ids() -> None:
    """A selection must resolve to exactly one trusted program definition."""
    with pytest.raises(ValidationError, match="Duplicate program id: BACHELOR"):
        ProgramCatalog.model_validate(
            {
                "catalog_version": "0.1",
                "programs": [
                    {
                        "id": "BACHELOR",
                        "display_name": "First",
                        "study_level": "BACHELOR",
                        "program_subject": "COMPUTER_SCIENCE",
                        "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
                    },
                    {
                        "id": "BACHELOR",
                        "display_name": "Second",
                        "study_level": "BACHELOR",
                        "program_subject": "COMPUTER_SCIENCE",
                        "policy": {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"},
                    },
                ],
            }
        )
