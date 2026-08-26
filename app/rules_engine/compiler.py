"""Strict YAML loading, reference resolution, and policy compilation."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

from pydantic import JsonValue, TypeAdapter, ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
from ruamel.yaml.error import YAMLError

from app.models.compiled_policy import (
    AllExpression,
    AnyExpression,
    ApplicabilityDefinition,
    AtomicExpression,
    BranchDefinition,
    BranchGroupDefinition,
    CompiledPolicy,
    Expression,
    RequirementDefinition,
    ResolutionDefinition,
    ResultDefinition,
    RuleDefinition,
)
from app.models.facts import (
    AccessScope,
    AdvancedVocationalType,
    IssuingRegion,
    SchoolQualificationType,
    SubjectRelationship,
    ValidityRestrictionCode,
    VocationalTrainingType,
)
from app.models.policy_specs import (
    AllApplicableResolutionSpec,
    AllExpressionSpec,
    AnyExpressionSpec,
    AnyRuleResolutionSpec,
    AtomicExpressionSpec,
    ExpressionSpec,
    ModuleDocumentSpec,
    NoRecognizedRuleResolutionSpec,
    PolicyDocumentSpec,
    ReferenceSpec,
    ResultSpec,
    RuleGroupSpec,
)
from app.models.results import (
    RULE_ORDER,
    ApplicationStatus,
    EntryCondition,
    RuleId,
    RuleStatus,
)
from app.rules_engine.comparisons import Operator, compile_comparison
from app.rules_engine.errors import PolicyActivationError
from app.rules_engine.reason_catalog import RULE_EXPLANATIONS

_EXPRESSION_ADAPTER: TypeAdapter[ExpressionSpec] = TypeAdapter(ExpressionSpec)


@dataclass(frozen=True, slots=True)
class _FactSpec:
    """The primitive kind and, for enum-backed facts, the exact value domain."""

    kind: type[bool] | type[int] | type[str]
    domain: frozenset[str] | None = None


def _enum(*members: type[StrEnum]) -> frozenset[str]:
    return frozenset(member.value for enum in members for member in enum)


_APPLICATION_FACTS: dict[str, _FactSpec] = {
    "application.study_level": _FactSpec(str, frozenset({"BACHELOR"})),
}

_SOURCE_FACTS: dict[str, dict[str, _FactSpec]] = {
    "school_qualifications": {
        "qualification.type": _FactSpec(str, _enum(SchoolQualificationType)),
        "qualification.country": _FactSpec(str),
        "qualification.completed": _FactSpec(bool),
        "qualification.access_scope": _FactSpec(str, _enum(AccessScope)),
        "qualification.validity_restriction_present": _FactSpec(bool),
        "qualification.validity_restriction_code": _FactSpec(str, _enum(ValidityRestrictionCode)),
        "qualification.school_part_proven": _FactSpec(bool),
        "qualification.vocational_part_proven": _FactSpec(bool),
        "qualification.issuing_region": _FactSpec(str, _enum(IssuingRegion)),
    },
    "advanced_vocational_qualifications": {
        "qualification.type": _FactSpec(str, _enum(AdvancedVocationalType)),
        "qualification.country": _FactSpec(str),
        "qualification.completed": _FactSpec(bool),
        "qualification.dqr_or_eqr_level": _FactSpec(int),
        "qualification.teaching_hours": _FactSpec(int),
        "qualification.builds_on_completed_training": _FactSpec(bool),
        "qualification.builds_on_recognized_training": _FactSpec(bool),
    },
    "professional_access_candidates": {
        "candidate.training.type": _FactSpec(str, _enum(VocationalTrainingType)),
        "candidate.training.country": _FactSpec(str),
        "candidate.training.completed": _FactSpec(bool),
        "candidate.training.recognized": _FactSpec(bool),
        "candidate.training.duration_months": _FactSpec(int),
        "candidate.training.dqr_or_eqr_level": _FactSpec(int),
        "candidate.all_period_dates_known": _FactSpec(bool),
        "candidate.all_weekly_hours_known": _FactSpec(bool),
        "candidate.mini_job_classification_complete": _FactSpec(bool),
        "candidate.full_time_equivalent_days_after_training": _FactSpec(int),
        "candidate.subject_relationship": _FactSpec(str, _enum(SubjectRelationship)),
    },
}

_SOURCE_ALIAS: dict[str, str] = {
    "school_qualifications": "qualification",
    "advanced_vocational_qualifications": "qualification",
    "professional_access_candidates": "candidate",
}

_ALL_FACT_PATHS: frozenset[str] = frozenset(_APPLICATION_FACTS).union(*(set(f) for f in _SOURCE_FACTS.values()))


@dataclass(frozen=True, slots=True)
class _LoadedModule:
    path: Path
    document: ModuleDocumentSpec


class PolicyCompiler:
    """Load and eagerly compile one policy package rooted at a directory."""

    def __init__(self, rules_root: Path, entry: Path) -> None:
        """Initialize a compiler for one policy document inside a trusted rules root."""
        self._root = rules_root.resolve()
        self._entry = entry
        self._namespaces: dict[str, _LoadedModule] = {}
        self._loaded_by_path: dict[Path, _LoadedModule] = {}
        self._module_ids: dict[str, Path] = {}
        self._comparison_number = 0

    def compile(self) -> CompiledPolicy:
        """Compile the configured policy document or raise a typed activation error."""
        entry = self._entry
        raw = self._read_yaml(entry)
        try:
            policy_document = PolicyDocumentSpec.model_validate(raw)
        except ValidationError as error:
            raise PolicyActivationError("INVALID_POLICY_SCHEMA", "The root policy does not match DSL 1.3") from error

        self._load_imports(entry, policy_document.policy.imports, ())
        self._validate_required_namespaces()
        policy = policy_document.policy

        applies_when = self._compile_expression(
            policy.applies_when,
            context="policy.applies_when",
            facts=_APPLICATION_FACTS,
            reference_stack=(),
        )
        rules = self._compile_rules(policy)
        resolution = self._compile_resolution(policy)
        return CompiledPolicy(
            policy_id=policy.id,
            version=policy.version,
            applies_when=applies_when,
            rules=rules,
            resolution=resolution,
        )

    def _read_yaml(self, path: Path) -> Any:
        return _read_policy_yaml(self._root, path)

    def _load_imports(self, declaring_path: Path, imports: tuple[Any, ...], stack: tuple[Path, ...]) -> None:
        declaring_resolved = declaring_path.resolve()
        if declaring_resolved in stack:
            raise PolicyActivationError("CYCLIC_POLICY_IMPORT", "Policy imports contain a cycle")
        next_stack = (*stack, declaring_resolved)
        local_namespaces: set[str] = set()

        for import_spec in imports:
            if import_spec.namespace in local_namespaces:
                raise PolicyActivationError("DUPLICATE_NAMESPACE", "A policy file imports one namespace more than once")
            local_namespaces.add(import_spec.namespace)
            imported_path = (declaring_resolved.parent / import_spec.file).resolve()
            if not imported_path.is_relative_to(self._root):
                raise PolicyActivationError("POLICY_PATH_ESCAPE", "A policy import escapes the configured rules root")
            if imported_path in next_stack:
                raise PolicyActivationError("CYCLIC_POLICY_IMPORT", "Policy imports contain a cycle")

            loaded = self._loaded_by_path.get(imported_path)
            if loaded is None:
                raw = self._read_yaml(imported_path)
                try:
                    document = ModuleDocumentSpec.model_validate(raw)
                except ValidationError as error:
                    raise PolicyActivationError(
                        "INVALID_MODULE_SCHEMA", "An imported policy module does not match DSL 1.3"
                    ) from error
                existing_id_path = self._module_ids.get(document.module.id)
                if existing_id_path is not None and existing_id_path != imported_path:
                    raise PolicyActivationError("DUPLICATE_MODULE_ID", "Two policy modules declare the same identifier")
                self._module_ids[document.module.id] = imported_path
                loaded = _LoadedModule(path=imported_path, document=document)
                self._loaded_by_path[imported_path] = loaded
                self._load_imports(imported_path, document.module.imports, next_stack)

            previous = self._namespaces.get(import_spec.namespace)
            if previous is not None and previous.path != imported_path:
                raise PolicyActivationError("DUPLICATE_NAMESPACE", "One namespace refers to different policy modules")
            self._namespaces[import_spec.namespace] = loaded

    def _validate_required_namespaces(self) -> None:
        available = set(self._namespaces)
        for loaded in self._loaded_by_path.values():
            missing = set(loaded.document.module.requires_namespaces).difference(available)
            if missing:
                raise PolicyActivationError("UNRESOLVED_NAMESPACE", "A policy module requires an unknown namespace")

    def _export(self, reference: str) -> Any:
        namespace, name = reference.split(".", maxsplit=1)
        module = self._namespaces.get(namespace)
        if module is None:
            raise PolicyActivationError("UNRESOLVED_REFERENCE", "A policy reference uses an unknown namespace")
        if name not in module.document.module.exports:
            raise PolicyActivationError("UNRESOLVED_REFERENCE", "A policy reference uses an unknown export")
        return module.document.module.exports[name]

    def _compile_rules(self, policy: Any) -> tuple[RuleDefinition, ...]:
        rule_specs: list[Any] = []
        for group_reference in policy.evaluation.rule_groups:
            try:
                group = RuleGroupSpec.model_validate(self._export(group_reference.include))
            except ValidationError as error:
                raise PolicyActivationError("INVALID_RULE_GROUP", "A rule group does not match DSL 1.3") from error
            rule_specs.extend(group.rules)

        ids = tuple(rule.id for rule in rule_specs)
        if len(ids) != len(set(ids)):
            raise PolicyActivationError("DUPLICATE_RULE_ID", "The policy contains a duplicate rule identifier")
        if set(ids) != {rule.value for rule in RULE_ORDER}:
            raise PolicyActivationError("UNSUPPORTED_RULE", "The policy does not contain the five supported rules")

        compiled_by_id: dict[RuleId, RuleDefinition] = {}
        for rule_spec in rule_specs:
            try:
                rule_id = RuleId(rule_spec.id)
            except ValueError as error:
                raise PolicyActivationError("UNSUPPORTED_RULE", "The policy contains an unsupported rule") from error
            if rule_spec.select.as_ != _SOURCE_ALIAS[rule_spec.select.from_]:
                raise PolicyActivationError("INVALID_SELECTOR_ALIAS", "A rule selector uses the wrong candidate alias")
            facts = _SOURCE_FACTS[rule_spec.select.from_]
            context = f"rule.{rule_id.value}"
            selector = self._compile_expression(
                rule_spec.select.where,
                context=f"{context}.select",
                facts=facts,
                reference_stack=(),
            )
            applicability = None
            if rule_spec.applicability is not None:
                applicability = ApplicabilityDefinition(
                    expression=self._compile_expression(
                        rule_spec.applicability.require,
                        context=f"{context}.applicability",
                        facts=facts,
                        reference_stack=(),
                    ),
                    not_applicable=self._compile_result(rule_spec.applicability.result.not_applicable),
                    unknown=self._compile_result(rule_spec.applicability.result.unknown),
                )

            requirement = None
            if rule_spec.require is not None and rule_spec.result is not None:
                requirement = RequirementDefinition(
                    expression=self._compile_expression(
                        rule_spec.require,
                        context=f"{context}.require",
                        facts=facts,
                        reference_stack=(),
                    ),
                    satisfied=self._compile_result(rule_spec.result.satisfied),
                    not_satisfied=self._compile_result(rule_spec.result.not_satisfied),
                    unknown=self._compile_result(rule_spec.result.unknown),
                )

            branches = None
            if rule_spec.branches is not None:
                branches = BranchGroupDefinition(
                    first_match=tuple(
                        BranchDefinition(
                            when=self._compile_expression(
                                branch.when,
                                context=f"{context}.branch.{index}",
                                facts=facts,
                                reference_stack=(),
                            ),
                            result=self._compile_result(branch.result),
                        )
                        for index, branch in enumerate(rule_spec.branches.first_match, start=1)
                    ),
                    unknown=self._compile_result(rule_spec.branches.unknown.result),
                    otherwise=self._compile_result(rule_spec.branches.otherwise.result),
                )

            compiled_by_id[rule_id] = RuleDefinition(
                rule_id=rule_id,
                source=rule_spec.select.from_,
                alias=rule_spec.select.as_,
                selector=selector,
                applicability=applicability,
                requirement=requirement,
                branches=branches,
            )

        return tuple(compiled_by_id[rule_id] for rule_id in RULE_ORDER)

    def _compile_expression(
        self,
        specification: ExpressionSpec,
        *,
        context: str,
        facts: Mapping[str, _FactSpec],
        reference_stack: tuple[str, ...],
    ) -> Expression:
        if isinstance(specification, ReferenceSpec):
            if specification.ref in reference_stack:
                raise PolicyActivationError("CYCLIC_REFERENCE", "Policy requirement references contain a cycle")
            try:
                resolved = _EXPRESSION_ADAPTER.validate_python(self._export(specification.ref))
            except ValidationError as error:
                raise PolicyActivationError(
                    "INVALID_REFERENCE_TARGET", "A requirement reference is not an expression"
                ) from error
            return self._compile_expression(
                resolved,
                context=f"{context}.{specification.ref}",
                facts=facts,
                reference_stack=(*reference_stack, specification.ref),
            )
        if isinstance(specification, AllExpressionSpec):
            return AllExpression(
                children=tuple(
                    self._compile_expression(
                        child,
                        context=f"{context}.all.{index}",
                        facts=facts,
                        reference_stack=reference_stack,
                    )
                    for index, child in enumerate(specification.all_of, start=1)
                )
            )
        if isinstance(specification, AnyExpressionSpec):
            return AnyExpression(
                children=tuple(
                    self._compile_expression(
                        child,
                        context=f"{context}.any.{index}",
                        facts=facts,
                        reference_stack=reference_stack,
                    )
                    for index, child in enumerate(specification.any_of, start=1)
                )
            )
        if not isinstance(specification, AtomicExpressionSpec):
            raise PolicyActivationError("INVALID_EXPRESSION", "The policy contains an unsupported expression")
        fact_spec = facts.get(specification.fact)
        if fact_spec is None:
            if specification.fact in _ALL_FACT_PATHS:
                raise PolicyActivationError(
                    "INVALID_FACT_PATH", "A policy expression uses a fact its candidate collection cannot supply"
                )
            raise PolicyActivationError("UNKNOWN_FACT_PATH", "A policy expression uses an unknown fact path")

        operator, expected = self._operator_and_expected(specification)
        self._validate_expected(fact_spec, operator, expected)
        self._comparison_number += 1
        return AtomicExpression(
            comparison_id=f"comparison:{self._comparison_number:04d}:{context}",
            fact_path=specification.fact,
            operator=operator,
            expected=expected,
            comparison=compile_comparison(operator, expected),
        )

    @staticmethod
    def _operator_and_expected(specification: AtomicExpressionSpec) -> tuple[Operator, Any]:
        if "eq" in specification.model_fields_set:
            return "eq", specification.eq
        if "in_" in specification.model_fields_set:
            return "in", specification.in_
        if "gte" in specification.model_fields_set:
            return "gte", specification.gte
        return "lt", specification.lt

    @staticmethod
    def _validate_expected(fact_spec: _FactSpec, operator: Operator, expected: Any) -> None:
        values = expected if operator == "in" else (expected,)
        if not isinstance(values, tuple) or not values:
            raise PolicyActivationError("INVALID_COMPARISON_TYPE", "A policy comparison has an invalid expected value")
        if any(type(value) is not fact_spec.kind for value in values):
            raise PolicyActivationError("INVALID_COMPARISON_TYPE", "A policy comparison uses the wrong value type")
        if operator in {"gte", "lt"} and fact_spec.kind is not int:
            raise PolicyActivationError("INVALID_COMPARISON_TYPE", "Threshold operators require an integer fact")
        if fact_spec.domain is not None and any(value not in fact_spec.domain for value in values):
            raise PolicyActivationError(
                "UNKNOWN_FACT_VALUE", "A policy comparison uses a value outside the fact domain"
            )

    def _compile_result(self, result: ResultSpec) -> ResultDefinition:
        raw_status = self._export(result.status.ref)
        try:
            status = RuleStatus(raw_status)
        except ValueError as error:
            raise PolicyActivationError("INVALID_RULE_STATUS", "A rule result references an invalid status") from error

        condition = None
        if result.condition is not None:
            raw_condition = self._export(result.condition)
            if not isinstance(raw_condition, dict):
                raise PolicyActivationError("INVALID_CONDITION", "A policy condition must be a mapping")
            condition_id = result.condition.split(".", maxsplit=1)[1]
            try:
                condition = EntryCondition(
                    id=condition_id,
                    parameters=cast(dict[str, JsonValue], raw_condition),
                )
            except ValidationError as error:
                raise PolicyActivationError(
                    "INVALID_CONDITION", "A policy condition contains invalid values"
                ) from error
        if result.reason_code not in RULE_EXPLANATIONS:
            raise PolicyActivationError(
                "UNKNOWN_REASON_CODE", "A rule result uses a reason code with no configured explanation"
            )
        return ResultDefinition(status=status, reason_code=result.reason_code, condition=condition)

    def _compile_resolution(self, policy: Any) -> tuple[ResolutionDefinition, ...]:
        definitions: list[ResolutionDefinition] = []
        for case in policy.resolution.first_match:
            raw_application_status = self._export(case.application_status.ref)
            try:
                application_status = ApplicationStatus(raw_application_status)
            except ValueError as error:
                raise PolicyActivationError(
                    "INVALID_APPLICATION_STATUS", "Resolution references an invalid status"
                ) from error
            if isinstance(case, AnyRuleResolutionSpec):
                definitions.append(
                    ResolutionDefinition(
                        kind="ANY_RULE",
                        rule_status=self._rule_status(case.when_any_rule.ref),
                        application_status=application_status,
                    )
                )
            elif isinstance(case, AllApplicableResolutionSpec):
                definitions.append(
                    ResolutionDefinition(
                        kind="ALL_APPLICABLE",
                        rule_status=self._rule_status(case.when_all_applicable_rules.ref),
                        application_status=application_status,
                    )
                )
            elif isinstance(case, NoRecognizedRuleResolutionSpec):
                definitions.append(
                    ResolutionDefinition(
                        kind="NO_RECOGNIZED_RULE",
                        rule_status=None,
                        application_status=application_status,
                    )
                )
        if not definitions or definitions[-1].kind != "NO_RECOGNIZED_RULE":
            raise PolicyActivationError("INVALID_RESOLUTION", "Resolution must end with no recognized rule")
        return tuple(definitions)

    def _rule_status(self, reference: str) -> RuleStatus:
        raw_status = self._export(reference)
        try:
            return RuleStatus(raw_status)
        except ValueError as error:
            raise PolicyActivationError(
                "INVALID_RULE_STATUS", "Resolution references an invalid rule status"
            ) from error


def _read_policy_yaml(root: Path, path: Path) -> Any:
    """Read one trusted YAML document from inside the configured rules root."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise PolicyActivationError("POLICY_PATH_ESCAPE", "A policy import escapes the configured rules root")
    if resolved.suffix != ".yaml":
        raise PolicyActivationError("INVALID_POLICY_IMPORT", "Policy imports must reference YAML files")
    if not resolved.is_file():
        raise PolicyActivationError("POLICY_IMPORT_NOT_FOUND", "A policy import could not be found")

    yaml = YAML(typ="safe")
    yaml.allow_duplicate_keys = False
    try:
        with resolved.open("r", encoding="utf-8") as stream:
            return yaml.load(stream)
    except DuplicateKeyError as error:
        raise PolicyActivationError("DUPLICATE_YAML_KEY", "A policy file contains a duplicate key") from error
    except (OSError, ValueError, YAMLError) as error:
        raise PolicyActivationError("INVALID_POLICY_YAML", "A policy file could not be read") from error


def compile_policy_package(rules_root: Path) -> dict[str, CompiledPolicy]:
    """Compile every policy document in one trusted rules package.

    Args:
        rules_root: Trusted directory containing the DSL 1.3 policy package.

    Returns:
        Every activated policy keyed by its own declared policy identifier.

    Raises:
        PolicyActivationError: If the package is empty or any definition is invalid.
    """
    root = rules_root.resolve()
    if not root.is_dir():
        raise PolicyActivationError("RULES_ROOT_NOT_FOUND", "The configured rules root is not a directory")

    compiled: dict[str, CompiledPolicy] = {}
    for entry in sorted(root.glob("*.yaml")):
        document = _read_policy_yaml(root, entry)
        if not isinstance(document, dict) or "policy" not in document:
            continue
        policy = PolicyCompiler(root, entry).compile()
        if policy.policy_id in compiled:
            raise PolicyActivationError("DUPLICATE_POLICY_ID", "The rules package declares a duplicate policy id")
        compiled[policy.policy_id] = policy

    if not compiled:
        raise PolicyActivationError("NO_POLICY_DEFINED", "The configured rules root contains no policy document")
    return compiled
