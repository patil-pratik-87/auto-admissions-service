from pathlib import Path

from app.models.artifacts import ApplicationFactsArtifact
from app.models.outcomes import EvaluationSucceeded
from app.models.results import RULE_ORDER, ApplicationStatus, RuleStatus
from app.rules_engine import RulesEngine


def test_no_recognized_qualification_requires_manual_review(
    rules_root: Path,
    empty_artifact: ApplicationFactsArtifact,
) -> None:
    module = RulesEngine.activate(rules_root)

    outcome = module.evaluate(empty_artifact)

    assert isinstance(outcome, EvaluationSucceeded)
    assert outcome.result.run_id == "run-decision-001"
    assert outcome.result.application_status is ApplicationStatus.MANUAL_REVIEW
    assert outcome.result.application_reason_code == "NO_RECOGNIZED_ADMISSIONS_RULE"
    assert tuple(rule.rule_id for rule in outcome.result.rules) == RULE_ORDER
    assert {rule.status for rule in outcome.result.rules} == {RuleStatus.NOT_APPLICABLE}
    assert outcome.result.summary.canonical.headline == "Academic access requires manual review"
