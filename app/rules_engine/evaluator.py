"""Pure evidence-aware evaluation and deterministic result composition."""

from collections import Counter
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal, cast

import rule_engine as zerosteiner
from pydantic import BaseModel

from app.models.artifacts import ApplicationFactsArtifact
from app.models.compiled_policy import (
    AllExpression,
    AnyExpression,
    CompiledPolicy,
    Expression,
    ResultDefinition,
    RuleDefinition,
)
from app.models.documents import DocumentManifest
from app.models.facts import (
    ConflictingFact,
    EvidenceRef,
    KnownFact,
    MissingFact,
    UnreadableFact,
)
from app.models.programs import PolicyRef
from app.models.results import (
    ApplicationResult,
    ApplicationStatus,
    CanonicalSummary,
    EntryCondition,
    EvidencePointer,
    ManualReviewItem,
    MissingInformationItem,
    ProgramRef,
    ResultSummary,
    RuleId,
    RuleResult,
    RuleStatus,
)
from app.rules_engine.errors import EvaluationInputError
from app.rules_engine.reason_catalog import (
    APPLICATION_HEADLINES,
    APPLICATION_REASON_CODES,
    FACT_LABELS,
    RULE_EXPLANATIONS,
)
from app.rules_engine.truth import TruthValue, conjunction, disjunction


@dataclass(frozen=True, slots=True)
class _FactView:
    path: str
    fact_id: str
    state: Literal["KNOWN", "MISSING", "UNREADABLE", "CONFLICTING"]
    value: Any
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class _Candidate:
    candidate_id: str
    facts: dict[str, _FactView]


@dataclass(frozen=True, slots=True)
class _ExpressionEvaluation:
    truth: TruthValue
    facts: tuple[_FactView, ...]


@dataclass(frozen=True, slots=True)
class _CandidateEvaluation:
    candidate_id: str
    result: ResultDefinition
    facts: tuple[_FactView, ...]


@dataclass(frozen=True, slots=True)
class _RuleEvaluation:
    rule_id: RuleId
    status: RuleStatus
    reason_code: str
    candidate_ids: tuple[str, ...]
    facts: tuple[_FactView, ...]
    condition: EntryCondition | None


type _EvidenceIndex = dict[tuple[str, int, str | None], tuple[str, EvidencePointer]]


_RULE_PRECEDENCE: dict[RuleStatus, int] = {
    RuleStatus.ELIGIBLE: 5,
    RuleStatus.CONDITIONALLY_ELIGIBLE: 4,
    RuleStatus.MANUAL_REVIEW: 3,
    RuleStatus.MISSING_INFORMATION: 2,
    RuleStatus.NOT_SATISFIED: 1,
    RuleStatus.NOT_APPLICABLE: 0,
}


def evaluate_policy(policy: CompiledPolicy, artifact: ApplicationFactsArtifact) -> ApplicationResult:
    """Evaluate one saved artifact against one already activated policy."""
    _validate_artifact(policy, artifact)
    candidates = _build_candidates(artifact)
    trusted_context = {
        "application.study_level": _FactView(
            path="application.study_level",
            fact_id="trusted:application.study_level",
            state="KNOWN",
            value=artifact.program.study_level,
            evidence=(),
        )
    }
    if _evaluate_expression(policy.applies_when, trusted_context).truth is not TruthValue.TRUE:
        raise EvaluationInputError("POLICY_NOT_APPLICABLE", "The saved program context is outside the active policy")

    rule_evaluations = tuple(_evaluate_rule(rule, candidates[rule.source]) for rule in policy.rules)
    application_status, application_reason_code, decisive = _resolve_application(policy, rule_evaluations)
    evidence_index = _evidence_index(rule_evaluations, artifact.manifest)
    rule_reports = tuple(_rule_result(rule, evidence_index) for rule in rule_evaluations)
    missing_information = _missing_information(rule_evaluations, evidence_index)
    manual_review = _manual_review(rule_evaluations, application_status, decisive, evidence_index)
    evidence = _evidence_pointers(evidence_index)
    summary = _canonical_summary(
        application_status,
        decisive,
        rule_evaluations,
        missing_information,
    )
    return ApplicationResult(
        kind="APPLICATION_RESULT",
        result_version="2.0",
        run_id=artifact.run_id,
        scope="ACADEMIC_ACCESS_ONLY",
        program=ProgramRef(id=artifact.program.program_id, display_name=artifact.program.display_name),
        policy=PolicyRef(id=policy.policy_id, version=policy.version),
        application_status=application_status,
        application_reason_code=application_reason_code,
        rules=rule_reports,
        missing_information=missing_information,
        manual_review=manual_review,
        warnings=artifact.warnings,
        evidence=evidence,
        summary=ResultSummary(canonical=summary, llm_paraphrase=None),
    )


def _validate_artifact(policy: CompiledPolicy, artifact: ApplicationFactsArtifact) -> None:
    if artifact.program.policy.id != policy.policy_id or artifact.program.policy.version != policy.version:
        raise EvaluationInputError("POLICY_VERSION_MISMATCH", "The saved facts reference a different policy")

    manifest_pages = {document.document_id: document.page_count for document in artifact.manifest.documents}
    for fact in _iter_facts(artifact.facts):
        for reference in _fact_evidence(fact):
            page_count = manifest_pages.get(reference.document_id)
            if page_count is None or reference.page_number > page_count:
                raise EvaluationInputError(
                    "INVALID_EVIDENCE_REFERENCE", "A fact references evidence outside the manifest"
                )


def _iter_facts(value: object) -> list[Any]:
    if isinstance(value, (KnownFact, MissingFact, UnreadableFact, ConflictingFact)):
        return [value]
    if isinstance(value, BaseModel):
        found: list[Any] = []
        for field_name in type(value).model_fields:
            found.extend(_iter_facts(getattr(value, field_name)))
        return found
    if isinstance(value, (tuple, list)):
        found = []
        for item in value:
            found.extend(_iter_facts(item))
        return found
    return []


def _fact_evidence(fact: Any) -> tuple[EvidenceRef, ...]:
    if isinstance(fact, ConflictingFact):
        return tuple(reference for candidate in fact.candidates for reference in candidate.evidence)
    return tuple(fact.evidence)


def _fact_view(path: str, fact: Any) -> _FactView:
    value = fact.value if isinstance(fact, KnownFact) else None
    return _FactView(
        path=path,
        fact_id=fact.fact_id,
        state=fact.state,
        value=value,
        evidence=_fact_evidence(fact),
    )


def _build_candidates(artifact: ApplicationFactsArtifact) -> dict[str, tuple[_Candidate, ...]]:
    facts = artifact.facts
    school_candidates = tuple(
        _Candidate(
            candidate_id=qualification.qualification_id,
            facts={
                "qualification.type": _fact_view("qualification.type", qualification.type),
                "qualification.country": _fact_view("qualification.country", qualification.country),
                "qualification.completed": _fact_view("qualification.completed", qualification.completed),
                "qualification.access_scope": _fact_view("qualification.access_scope", qualification.access_scope),
                "qualification.validity_restriction_present": _fact_view(
                    "qualification.validity_restriction_present", qualification.validity_restriction_present
                ),
                "qualification.validity_restriction_code": _fact_view(
                    "qualification.validity_restriction_code", qualification.validity_restriction_code
                ),
                "qualification.school_part_proven": _fact_view(
                    "qualification.school_part_proven", qualification.school_part_proven
                ),
                "qualification.vocational_part_proven": _fact_view(
                    "qualification.vocational_part_proven", qualification.vocational_part_proven
                ),
                "qualification.issuing_region": _fact_view(
                    "qualification.issuing_region",
                    qualification.issuing_region,
                ),
            },
        )
        for qualification in sorted(facts.school_qualifications, key=lambda item: item.qualification_id)
    )

    advanced_candidates = tuple(
        _Candidate(
            candidate_id=qualification.qualification_id,
            facts={
                "qualification.type": _fact_view("qualification.type", qualification.type),
                "qualification.country": _fact_view("qualification.country", qualification.country),
                "qualification.completed": _fact_view("qualification.completed", qualification.completed),
                "qualification.dqr_or_eqr_level": _fact_view(
                    "qualification.dqr_or_eqr_level", qualification.dqr_or_eqr_level
                ),
                "qualification.teaching_hours": _fact_view(
                    "qualification.teaching_hours", qualification.teaching_hours
                ),
                "qualification.builds_on_completed_training": _fact_view(
                    "qualification.builds_on_completed_training", qualification.builds_on_completed_training
                ),
                "qualification.builds_on_recognized_training": _fact_view(
                    "qualification.builds_on_recognized_training", qualification.builds_on_recognized_training
                ),
            },
        )
        for qualification in sorted(
            facts.advanced_vocational_qualifications,
            key=lambda item: item.qualification_id,
        )
    )

    professional_candidates: list[_Candidate] = []
    for candidate in sorted(facts.professional_access_candidates, key=lambda item: item.candidate_id):
        training = candidate.training
        professional_candidates.append(
            _Candidate(
                candidate_id=candidate.candidate_id,
                facts={
                    "candidate.training.type": _fact_view("candidate.training.type", training.type),
                    "candidate.training.country": _fact_view("candidate.training.country", training.country),
                    "candidate.training.completed": _fact_view("candidate.training.completed", training.completed),
                    "candidate.training.recognized": _fact_view("candidate.training.recognized", training.recognized),
                    "candidate.training.duration_months": _fact_view(
                        "candidate.training.duration_months", training.duration_months
                    ),
                    "candidate.training.dqr_or_eqr_level": _fact_view(
                        "candidate.training.dqr_or_eqr_level", training.dqr_or_eqr_level
                    ),
                    "candidate.all_period_dates_known": _fact_view(
                        "candidate.all_period_dates_known", candidate.all_period_dates_known
                    ),
                    "candidate.all_weekly_hours_known": _fact_view(
                        "candidate.all_weekly_hours_known", candidate.all_weekly_hours_known
                    ),
                    "candidate.mini_job_classification_complete": _fact_view(
                        "candidate.mini_job_classification_complete", candidate.mini_job_classification_complete
                    ),
                    "candidate.full_time_equivalent_days_after_training": _fact_view(
                        "candidate.full_time_equivalent_days_after_training",
                        candidate.full_time_equivalent_days_after_training,
                    ),
                    "candidate.subject_relationship": _fact_view(
                        "candidate.subject_relationship", candidate.subject_relationship
                    ),
                },
            )
        )
    return {
        "school_qualifications": school_candidates,
        "advanced_vocational_qualifications": advanced_candidates,
        "professional_access_candidates": tuple(professional_candidates),
    }


def _evaluate_expression(expression: Expression, facts: dict[str, _FactView]) -> _ExpressionEvaluation:
    if isinstance(expression, AllExpression):
        children = tuple(_evaluate_expression(child, facts) for child in expression.children)
        return _ExpressionEvaluation(
            truth=conjunction(tuple(child.truth for child in children)),
            facts=_coalesce_facts(tuple(fact for child in children for fact in child.facts)),
        )
    if isinstance(expression, AnyExpression):
        children = tuple(_evaluate_expression(child, facts) for child in expression.children)
        return _ExpressionEvaluation(
            truth=disjunction(tuple(child.truth for child in children)),
            facts=_coalesce_facts(tuple(fact for child in children for fact in child.facts)),
        )

    fact = facts.get(expression.fact_path)
    if fact is None:
        raise EvaluationInputError("FACT_PATH_UNAVAILABLE", "The saved facts cannot satisfy an activated fact path")
    if fact.state != "KNOWN":
        return _ExpressionEvaluation(truth=TruthValue.UNKNOWN, facts=(fact,))
    try:
        matched = expression.comparison.matches(fact.value)
    except (TypeError, ValueError, zerosteiner.errors.EngineError) as error:
        raise EvaluationInputError("FACT_TYPE_MISMATCH", "A saved known fact has the wrong policy type") from error
    return _ExpressionEvaluation(
        truth=TruthValue.TRUE if matched else TruthValue.FALSE,
        facts=(fact,),
    )


def _evaluate_rule(rule: RuleDefinition, candidates: tuple[_Candidate, ...]) -> _RuleEvaluation:
    results: list[_CandidateEvaluation] = []
    for candidate in candidates:
        selector = _evaluate_expression(rule.selector, candidate.facts)
        if selector.truth is TruthValue.FALSE:
            continue
        if selector.truth is TruthValue.UNKNOWN:
            results.append(
                _CandidateEvaluation(
                    candidate_id=candidate.candidate_id,
                    result=_unknown_rule_result(rule),
                    facts=selector.facts,
                )
            )
            continue

        accumulated = selector.facts
        if rule.applicability is not None:
            applicability = _evaluate_expression(rule.applicability.expression, candidate.facts)
            accumulated = _coalesce_facts((*accumulated, *applicability.facts))
            if applicability.truth is TruthValue.FALSE:
                results.append(
                    _CandidateEvaluation(candidate.candidate_id, rule.applicability.not_applicable, accumulated)
                )
                continue
            if applicability.truth is TruthValue.UNKNOWN:
                results.append(_CandidateEvaluation(candidate.candidate_id, rule.applicability.unknown, accumulated))
                continue

        if rule.requirement is not None:
            requirement = _evaluate_expression(rule.requirement.expression, candidate.facts)
            accumulated = _coalesce_facts((*accumulated, *requirement.facts))
            selected = {
                TruthValue.TRUE: rule.requirement.satisfied,
                TruthValue.FALSE: rule.requirement.not_satisfied,
                TruthValue.UNKNOWN: rule.requirement.unknown,
            }[requirement.truth]
            results.append(_CandidateEvaluation(candidate.candidate_id, selected, accumulated))
            continue

        if rule.branches is None:
            raise EvaluationInputError("INVALID_COMPILED_RULE", "An activated rule has no evaluation body")
        branch_result, branch_facts = _evaluate_branches(rule, candidate)
        results.append(
            _CandidateEvaluation(
                candidate_id=candidate.candidate_id,
                result=branch_result,
                facts=_coalesce_facts((*accumulated, *branch_facts)),
            )
        )

    if not results:
        return _RuleEvaluation(
            rule_id=rule.rule_id,
            status=RuleStatus.NOT_APPLICABLE,
            reason_code="NO_CANDIDATE_FOR_RULE",
            candidate_ids=(),
            facts=(),
            condition=None,
        )

    highest = max(_RULE_PRECEDENCE[result.result.status] for result in results)
    winners = tuple(
        sorted(
            (result for result in results if _RULE_PRECEDENCE[result.result.status] == highest),
            key=lambda result: result.candidate_id,
        )
    )
    representative = winners[0]
    return _RuleEvaluation(
        rule_id=rule.rule_id,
        status=representative.result.status,
        reason_code=representative.result.reason_code,
        candidate_ids=tuple(result.candidate_id for result in winners),
        facts=_coalesce_facts(tuple(fact for result in winners for fact in result.facts)),
        condition=representative.result.condition,
    )


def _unknown_rule_result(rule: RuleDefinition) -> ResultDefinition:
    if rule.requirement is not None:
        return rule.requirement.unknown
    if rule.branches is not None:
        return rule.branches.unknown
    raise EvaluationInputError("INVALID_COMPILED_RULE", "An activated rule has no unknown result")


def _evaluate_branches(
    rule: RuleDefinition,
    candidate: _Candidate,
) -> tuple[ResultDefinition, tuple[_FactView, ...]]:
    if rule.branches is None:
        raise EvaluationInputError("INVALID_COMPILED_RULE", "An activated rule has no branches")
    accumulated: tuple[_FactView, ...] = ()
    for branch in rule.branches.first_match:
        evaluated = _evaluate_expression(branch.when, candidate.facts)
        accumulated = _coalesce_facts((*accumulated, *evaluated.facts))
        if evaluated.truth is TruthValue.FALSE:
            continue
        if evaluated.truth is TruthValue.UNKNOWN:
            return rule.branches.unknown, accumulated
        return branch.result, accumulated
    return rule.branches.otherwise, accumulated


def _coalesce_facts(facts: tuple[_FactView, ...]) -> tuple[_FactView, ...]:
    by_id: dict[str, _FactView] = {}
    for fact in facts:
        by_id.setdefault(fact.fact_id, fact)
    return tuple(by_id[fact_id] for fact_id in sorted(by_id))


def _resolve_application(
    policy: CompiledPolicy,
    rules: tuple[_RuleEvaluation, ...],
) -> tuple[ApplicationStatus, str, _RuleEvaluation | None]:
    """Select the first matching resolution case and the rule that decided it."""
    applicable = tuple(rule for rule in rules if rule.status is not RuleStatus.NOT_APPLICABLE)
    for resolution in policy.resolution:
        if resolution.kind == "NO_RECOGNIZED_RULE":
            if not applicable:
                return resolution.application_status, "NO_RECOGNIZED_ADMISSIONS_RULE", None
            continue
        decisive = next((rule for rule in applicable if rule.status is resolution.rule_status), None)
        if decisive is None:
            continue
        if resolution.kind == "ALL_APPLICABLE" and any(
            rule.status is not resolution.rule_status for rule in applicable
        ):
            continue
        return resolution.application_status, APPLICATION_REASON_CODES[resolution.application_status], decisive
    raise EvaluationInputError("POLICY_RESOLUTION_FAILED", "The active policy could not resolve the rule results")


def _rule_result(rule: _RuleEvaluation, index: _EvidenceIndex) -> RuleResult:
    evidence_ids = _sorted_evidence_ids(
        index[_reference_key(reference)][0] for fact in rule.facts for reference in _usable_evidence(fact)
    )
    return RuleResult(
        rule_id=rule.rule_id,
        status=rule.status,
        reason_code=rule.reason_code,
        candidate_ids=rule.candidate_ids,
        fact_ids=tuple(fact.fact_id for fact in rule.facts),
        evidence_ids=evidence_ids,
        condition=_condition_copy(rule.condition),
    )


def _condition_copy(condition: EntryCondition | None) -> EntryCondition | None:
    """Hand each result its own parameters so the activated policy stays immutable."""
    if condition is None:
        return None
    return EntryCondition(id=condition.id, parameters=deepcopy(condition.parameters))


def _missing_information(
    rules: tuple[_RuleEvaluation, ...],
    index: _EvidenceIndex,
) -> tuple[MissingInformationItem, ...]:
    grouped: dict[str, tuple[_FactView, set[RuleId]]] = {}
    for rule in rules:
        if rule.status not in {RuleStatus.MISSING_INFORMATION, RuleStatus.MANUAL_REVIEW}:
            continue
        for fact in rule.facts:
            if fact.state == "KNOWN":
                continue
            existing = grouped.get(fact.fact_id)
            if existing is None:
                grouped[fact.fact_id] = (fact, {rule.rule_id})
            else:
                existing[1].add(rule.rule_id)

    items: list[MissingInformationItem] = []
    for fact_id in sorted(grouped):
        fact, rule_ids = grouped[fact_id]
        evidence_ids = _sorted_evidence_ids(
            index[_reference_key(reference)][0] for reference in _usable_evidence(fact)
        )
        items.append(
            MissingInformationItem(
                fact_id=fact.fact_id,
                label=FACT_LABELS.get(fact.path, fact.path),
                state=cast(Literal["MISSING", "UNREADABLE", "CONFLICTING"], fact.state),
                rule_ids=tuple(rule_id for rule_id in RuleId if rule_id in rule_ids),
                evidence_ids=evidence_ids,
            )
        )
    return tuple(items)


def _manual_review(
    rules: tuple[_RuleEvaluation, ...],
    application_status: ApplicationStatus,
    decisive: _RuleEvaluation | None,
    index: _EvidenceIndex,
) -> tuple[ManualReviewItem, ...]:
    items = [
        ManualReviewItem(
            reason_code=rule.reason_code,
            explanation=RULE_EXPLANATIONS.get(rule.reason_code, "The configured rule requires human review."),
            rule_ids=(rule.rule_id,),
            evidence_ids=_sorted_evidence_ids(
                index[_reference_key(reference)][0] for fact in rule.facts for reference in _usable_evidence(fact)
            ),
        )
        for rule in rules
        if rule.status is RuleStatus.MANUAL_REVIEW
    ]
    if decisive is None and application_status is ApplicationStatus.MANUAL_REVIEW:
        items.append(
            ManualReviewItem(
                reason_code="NO_RECOGNIZED_ADMISSIONS_RULE",
                explanation="No submitted qualification matched a supported admissions rule.",
                rule_ids=(),
                evidence_ids=(),
            )
        )
    return tuple(items)


def _document_labels(manifest: DocumentManifest) -> dict[str, str]:
    """Map hashed document ids to unique human-readable filenames for the result."""
    name_counts = Counter(document.original_filename for document in manifest.documents)
    return {
        document.document_id: (
            document.original_filename
            if name_counts[document.original_filename] == 1
            else f"{document.original_filename}#{document.sha256[:8]}"
        )
        for document in manifest.documents
    }


def _evidence_index(rules: tuple[_RuleEvaluation, ...], manifest: DocumentManifest) -> _EvidenceIndex:
    """Assign deterministic short ids to the unique evidence references in use."""
    labels = _document_labels(manifest)
    references: dict[tuple[str, int, str | None], EvidenceRef] = {}
    for rule in rules:
        for fact in rule.facts:
            for reference in _usable_evidence(fact):
                references.setdefault(_reference_key(reference), reference)
    ordered = sorted(
        references.values(),
        key=lambda reference: (
            labels[reference.document_id],
            reference.page_number,
            reference.excerpt is not None,
            reference.excerpt or "",
        ),
    )
    index: _EvidenceIndex = {}
    for number, reference in enumerate(ordered, start=1):
        evidence_id = f"E{number}"
        index[_reference_key(reference)] = (
            evidence_id,
            EvidencePointer(
                evidence_id=evidence_id,
                document_id=labels[reference.document_id],
                page_number=reference.page_number,
                excerpt=reference.excerpt,
            ),
        )
    return index


def _reference_key(reference: EvidenceRef) -> tuple[str, int, str | None]:
    return (reference.document_id, reference.page_number, reference.excerpt)


def _sorted_evidence_ids(evidence_ids: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(evidence_ids), key=lambda evidence_id: int(evidence_id[1:])))


def _evidence_pointers(index: _EvidenceIndex) -> tuple[EvidencePointer, ...]:
    return tuple(pointer for _, pointer in sorted(index.values(), key=lambda item: int(item[0][1:])))


def _usable_evidence(fact: _FactView) -> tuple[EvidenceRef, ...]:
    return fact.evidence


def _canonical_summary(
    status: ApplicationStatus,
    decisive: _RuleEvaluation | None,
    rules: tuple[_RuleEvaluation, ...],
    missing_information: tuple[MissingInformationItem, ...],
) -> CanonicalSummary:
    if decisive is None:
        explanation = "None of the submitted qualifications matched one of the five supported admissions rules."
    else:
        explanation = RULE_EXPLANATIONS.get(
            decisive.reason_code, "The configured admissions policy produced this result."
        )
        if status in {ApplicationStatus.ELIGIBLE, ApplicationStatus.CONDITIONALLY_ELIGIBLE} and any(
            rule.status in {RuleStatus.MISSING_INFORMATION, RuleStatus.MANUAL_REVIEW} for rule in rules
        ):
            explanation += " Another rule remains incomplete, but it does not override the established rule."
    required_information = tuple(dict.fromkeys(item.label for item in missing_information))
    return CanonicalSummary(
        headline=APPLICATION_HEADLINES[status],
        explanation=explanation,
        required_information=required_information,
    )
