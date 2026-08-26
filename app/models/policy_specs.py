"""Strict Pydantic specifications for authored policy YAML."""

from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, model_validator


class SpecModel(BaseModel):
    """Strict immutable base for policy definition models."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ImportSpec(SpecModel):
    """One namespaced YAML import relative to its declaring file."""

    namespace: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    file: str = Field(min_length=1)


class ReferenceSpec(SpecModel):
    """Reference to one namespaced export."""

    ref: str = Field(pattern=r"^[a-z][a-z0-9_]*\.[A-Za-z][A-Za-z0-9_]*$")


type ScalarValue = StrictBool | StrictInt | StrictStr


class AtomicExpressionSpec(SpecModel):
    """One allowlisted authored scalar comparison."""

    fact: str = Field(pattern=r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
    eq: ScalarValue | None = None
    in_: tuple[ScalarValue, ...] | None = Field(default=None, alias="in", min_length=1)
    gte: StrictInt | None = None
    lt: StrictInt | None = None

    @model_validator(mode="after")
    def has_exactly_one_operator(self) -> Self:
        """Reject ambiguous or operator-free comparisons."""
        present = self.model_fields_set.intersection({"eq", "in_", "gte", "lt"})
        if len(present) != 1:
            raise ValueError("An atomic expression requires exactly one operator")
        return self


class AllExpressionSpec(SpecModel):
    """Non-empty authored conjunction."""

    all_of: tuple["ExpressionSpec", ...] = Field(min_length=1)


class AnyExpressionSpec(SpecModel):
    """Non-empty authored disjunction."""

    any_of: tuple["ExpressionSpec", ...] = Field(min_length=1)


type ExpressionSpec = AtomicExpressionSpec | AllExpressionSpec | AnyExpressionSpec | ReferenceSpec


class StatusSpec(SpecModel):
    """Namespaced status reference."""

    ref: str = Field(pattern=r"^[a-z][a-z0-9_]*\.[A-Z][A-Z0-9_]*$")


class ResultSpec(SpecModel):
    """One authored rule outcome."""

    status: StatusSpec
    reason_code: str = Field(pattern=r"^[A-Z][A-Z0-9_]*$")
    condition: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_]*\.[A-Z][A-Z0-9_]*$")


class ResultEnvelopeSpec(SpecModel):
    """Wrapper used by explicit branch fallbacks."""

    result: ResultSpec


class SelectSpec(SpecModel):
    """Candidate collection, alias, and selector."""

    from_: Literal[
        "school_qualifications",
        "advanced_vocational_qualifications",
        "professional_access_candidates",
    ] = Field(alias="from")
    as_: Literal["qualification", "candidate"] = Field(alias="as")
    where: ExpressionSpec


class ApplicabilityResultSpec(SpecModel):
    """Explicit results for false and unknown applicability."""

    not_applicable: ResultSpec
    unknown: ResultSpec


class ApplicabilitySpec(SpecModel):
    """Candidate applicability expression and outcomes."""

    require: ExpressionSpec
    result: ApplicabilityResultSpec


class RequirementResultSpec(SpecModel):
    """Explicit results for all three requirement truth values."""

    satisfied: ResultSpec
    not_satisfied: ResultSpec
    unknown: ResultSpec


class BranchSpec(SpecModel):
    """One ordered branch."""

    when: ExpressionSpec
    result: ResultSpec


class BranchGroupSpec(SpecModel):
    """Ordered branches with mandatory unknown and otherwise outcomes."""

    first_match: tuple[BranchSpec, ...] = Field(min_length=1)
    unknown: ResultEnvelopeSpec
    otherwise: ResultEnvelopeSpec


class RuleSpec(SpecModel):
    """One authored admissions rule."""

    id: str
    select: SelectSpec
    applicability: ApplicabilitySpec | None = None
    require: ExpressionSpec | None = None
    result: RequirementResultSpec | None = None
    branches: BranchGroupSpec | None = None

    @model_validator(mode="after")
    def has_one_body_shape(self) -> Self:
        """Require either a requirement result or an ordered branch group."""
        requirement_shape = self.require is not None and self.result is not None
        branch_shape = self.branches is not None
        if requirement_shape == branch_shape:
            raise ValueError("A rule requires exactly one requirement or branch body")
        if (self.require is None) != (self.result is None):
            raise ValueError("A rule requirement and result must appear together")
        return self


class RuleGroupSpec(SpecModel):
    """Named group of independently evaluated admissions rules."""

    id: str
    rules: tuple[RuleSpec, ...] = Field(min_length=1)


class ModuleBodySpec(SpecModel):
    """Generic definition module whose exports are validated by their use."""

    id: str
    version: str
    imports: tuple[ImportSpec, ...] = ()
    requires_namespaces: tuple[str, ...] = ()
    exports: dict[str, Any]


class ModuleDocumentSpec(SpecModel):
    """Strict top-level module document."""

    dsl_version: Literal["1.3"]
    module: ModuleBodySpec


class SourceSpec(SpecModel):
    """Non-executable provenance for an authored policy."""

    file: str
    section: str
    subsections: tuple[str, ...]


class RuleGroupIncludeSpec(SpecModel):
    """Reference to an imported rule group."""

    include: str = Field(pattern=r"^[a-z][a-z0-9_]*\.[A-Za-z][A-Za-z0-9_]*$")


class PolicyEvaluationSpec(SpecModel):
    """All-rules evaluation declaration."""

    rule_groups: tuple[RuleGroupIncludeSpec, ...] = Field(min_length=1)


class AnyRuleResolutionSpec(SpecModel):
    """Resolution case triggered by any rule status."""

    when_any_rule: StatusSpec
    application_status: StatusSpec


class AllApplicableResolutionSpec(SpecModel):
    """Resolution case triggered when every applicable rule has one status."""

    when_all_applicable_rules: StatusSpec
    application_status: StatusSpec


class NoRecognizedRuleResolutionSpec(SpecModel):
    """Resolution case used when every configured rule is not applicable."""

    when_no_recognized_rule: Literal[True]
    application_status: StatusSpec


type ResolutionCaseSpec = AnyRuleResolutionSpec | AllApplicableResolutionSpec | NoRecognizedRuleResolutionSpec


class ResolutionSpec(SpecModel):
    """Ordered final application resolution."""

    first_match: tuple[ResolutionCaseSpec, ...] = Field(min_length=1)


class PolicyBodySpec(SpecModel):
    """Executable root policy definition."""

    id: str
    version: str
    applies_when: ExpressionSpec
    sources: tuple[SourceSpec, ...]
    imports: tuple[ImportSpec, ...]
    evaluation: PolicyEvaluationSpec
    resolution: ResolutionSpec


class PolicyDocumentSpec(SpecModel):
    """Strict top-level policy document."""

    dsl_version: Literal["1.3"]
    policy: PolicyBodySpec


AllExpressionSpec.model_rebuild()
AnyExpressionSpec.model_rebuild()
