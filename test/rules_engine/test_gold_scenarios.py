from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from scenario_support import candidate_id, make_artifact

from app.models.outcomes import EvaluationSucceeded
from app.models.results import RULE_ORDER, ApplicationStatus, RuleStatus
from app.rules_engine import RulesEngine

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "rules_engine" / "scenarios.yaml"
REPRESENTATIVE_SCENARIO_IDS = (
    "01",
    "04",
    "05",
    "07",
    "09",
    "12",
    "13",
    "14",
    "16",
    "17",
    "19",
    "20",
    "22",
    "23",
    "24",
)


def _scenarios() -> list[dict[str, Any]]:
    loaded = YAML(typ="safe").load(FIXTURE_PATH)
    source: list[dict[str, Any]] = loaded["scenarios"]
    scenarios = [scenario for scenario in source if str(scenario["id"]) in REPRESENTATIVE_SCENARIO_IDS]
    assert tuple(str(scenario["id"]) for scenario in scenarios) == REPRESENTATIVE_SCENARIO_IDS
    return scenarios


@pytest.mark.parametrize("scenario", _scenarios(), ids=lambda scenario: str(scenario["id"]))
def test_representative_gold_scenarios_match_exact_policy_results(
    rules_root: Path,
    scenario: dict[str, Any],
) -> None:
    artifact = make_artifact(scenario)

    outcome = RulesEngine.activate(rules_root).evaluate(artifact)

    assert isinstance(outcome, EvaluationSucceeded)
    result = outcome.result
    expected = scenario["expected"]
    assert result.application_status is ApplicationStatus(expected["application_status"])
    assert result.application_reason_code == expected["application_reason_code"]
    assert tuple(rule.rule_id for rule in result.rules) == RULE_ORDER
    assert result.run_id == f"run-scenario-{scenario['id']}"
    assert result.policy.model_dump(mode="json") == {"id": "IU_BACHELOR_ACCESS", "version": "0.0.22"}
    assert result.summary.llm_paraphrase is None

    expected_rules = expected["rules"]
    for rule in result.rules:
        expected_rule = expected_rules.get(rule.rule_id.value)
        if expected_rule is None:
            assert rule.status is RuleStatus.NOT_APPLICABLE
            assert rule.reason_code == "NO_CANDIDATE_FOR_RULE"
            assert rule.candidate_ids == ()
            assert rule.condition is None
        else:
            assert rule.status is RuleStatus(expected_rule["status"])
            assert rule.reason_code == expected_rule["reason_code"]
            assert rule.candidate_ids == (candidate_id(str(scenario["id"]), expected_rule["candidate"]),)
            expected_condition = expected_rule.get("condition")
            actual_condition = None if rule.condition is None else rule.condition.model_dump(mode="json")
            assert actual_condition == expected_condition
            assert rule.fact_ids == tuple(sorted(set(rule.fact_ids)))


def test_representative_gold_corpus_exercises_every_public_application_status() -> None:
    scenarios = _scenarios()
    assert len(scenarios) == 15
    assert {scenario["expected"]["application_status"] for scenario in scenarios} == {
        "ELIGIBLE",
        "CONDITIONALLY_ELIGIBLE",
        "INELIGIBLE",
        "MISSING_INFORMATION",
        "MANUAL_REVIEW",
    }


def test_representative_gold_corpus_covers_every_rule_and_fact_state() -> None:
    scenarios = _scenarios()
    expected_rule_ids = {
        rule_id
        for scenario in scenarios
        for rule_id in scenario["expected"]["rules"]
    }
    assert expected_rule_ids == {rule.value for rule in RULE_ORDER}

    def collect_states(value: Any) -> set[str]:
        if isinstance(value, dict):
            own_state = {str(value["state"])} if "state" in value else set()
            return own_state.union(*(collect_states(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(collect_states(item) for item in value))
        return set()

    observed_states = set().union(
        *(collect_states(make_artifact(scenario).facts.model_dump(mode="json")) for scenario in scenarios)
    )
    assert observed_states == {"KNOWN", "MISSING", "UNREADABLE", "CONFLICTING"}


@pytest.mark.parametrize(
    "professional",
    (
        {"recognized": False},
        {"duration_months": 23},
        {"dqr_or_eqr_level": 3},
    ),
    ids=("unrecognized", "too-short", "level-below-four"),
)
def test_known_vocational_training_requirement_failure_is_not_reported_as_missing(
    rules_root: Path,
    professional: dict[str, Any],
) -> None:
    artifact = make_artifact({"id": "known-training-failure", "professional": professional})

    outcome = RulesEngine.activate(rules_root).evaluate(artifact)

    assert isinstance(outcome, EvaluationSucceeded)
    assert outcome.result.application_status is ApplicationStatus.INELIGIBLE
    rule = next(rule for rule in outcome.result.rules if rule.candidate_ids)
    assert rule.status is RuleStatus.NOT_SATISFIED
    assert rule.reason_code == "VOCATIONAL_TRAINING_REQUIREMENTS_NOT_MET"
