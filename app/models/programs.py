"""Trusted study-program catalog contracts."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator


class ContractModel(BaseModel):
    """Base configuration for immutable, strict program contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class PolicyRef(ContractModel):
    """Exact policy identity activated for a study program."""

    id: str
    version: str


class ProgramDefinition(ContractModel):
    """One selectable study program in the configured catalog."""

    id: str
    display_name: str
    study_level: Literal["BACHELOR"]
    program_subject: Literal["COMPUTER_SCIENCE"]
    policy: PolicyRef


class ProgramContext(ContractModel):
    """Trusted application context resolved from a selected program."""

    catalog_version: Literal["0.1"]
    program_id: str
    display_name: str
    study_level: Literal["BACHELOR"]
    program_subject: Literal["COMPUTER_SCIENCE"]
    policy: PolicyRef


class ProgramCatalog(ContractModel):
    """Versioned collection of selectable study programs."""

    catalog_version: Literal["0.1"]
    programs: tuple[ProgramDefinition, ...]

    @model_validator(mode="after")
    def program_ids_are_unique(self) -> Self:
        """Require each selectable program identifier to be unambiguous."""
        seen: set[str] = set()
        for program in self.programs:
            if program.id in seen:
                raise ValueError(f"Duplicate program id: {program.id}")
            seen.add(program.id)
        return self

    def resolve(self, program_id: str) -> ProgramContext:
        """Resolve a selected program into trusted application context.

        Args:
            program_id: Catalog program identifier selected by the user.

        Returns:
            The immutable trusted context for the selected program.

        Raises:
            ValueError: If the program identifier is not configured.
        """
        for program in self.programs:
            if program.id == program_id:
                return ProgramContext(
                    catalog_version=self.catalog_version,
                    program_id=program.id,
                    display_name=program.display_name,
                    study_level=program.study_level,
                    program_subject=program.program_subject,
                    policy=program.policy,
                )
        raise ValueError(f"Unknown program: {program_id}")
