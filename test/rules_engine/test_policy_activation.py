from pathlib import Path

import pytest

from app.rules_engine import PolicyActivationError, RulesEngine


def test_activation_rejects_an_unsupported_dsl_version(copied_rules: Path) -> None:
    policy_path = copied_rules / "bachelors-access.yaml"
    policy_path.write_text(
        policy_path.read_text(encoding="utf-8").replace('dsl_version: "1.3"', 'dsl_version: "9.9"', 1)
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "INVALID_POLICY_SCHEMA"


def test_activation_rejects_an_import_that_escapes_the_rules_root(copied_rules: Path) -> None:
    policy_path = copied_rules / "bachelors-access.yaml"
    policy_path.write_text(
        policy_path.read_text(encoding="utf-8").replace("file: application-statuses.yaml", "file: ../../outside.yaml")
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "POLICY_PATH_ESCAPE"


def test_activation_rejects_an_unresolved_requirement_reference(copied_rules: Path) -> None:
    rule_path = copied_rules / "school-access-rules.yaml"
    rule_path.write_text(
        rule_path.read_text(encoding="utf-8").replace(
            "requirements.completed_school_qualification",
            "requirements.not_defined",
        )
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "UNRESOLVED_REFERENCE"


def test_activation_rejects_a_cyclic_requirement_reference(copied_rules: Path) -> None:
    requirement_path = copied_rules / "common" / "requirements.yaml"
    requirement_path.write_text(
        requirement_path.read_text(encoding="utf-8").replace(
            "completed_school_qualification:\n      fact: qualification.completed\n      eq: true",
            "completed_school_qualification:\n      ref: requirements.completed_school_qualification",
        )
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "CYCLIC_REFERENCE"


def test_activation_rejects_an_unsupported_expression_operator(copied_rules: Path) -> None:
    requirement_path = copied_rules / "common" / "requirements.yaml"
    requirement_path.write_text(
        requirement_path.read_text(encoding="utf-8").replace("      eq: true", "      gt: true", 1)
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "INVALID_REFERENCE_TARGET"


def test_activation_rejects_duplicate_rule_identifiers(copied_rules: Path) -> None:
    rule_path = copied_rules / "professional-access-rules.yaml"
    rule_path.write_text(
        rule_path.read_text(encoding="utf-8").replace(
            "id: GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL",
            "id: GERMAN_ABITUR",
            1,
        )
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "DUPLICATE_RULE_ID"


def test_activation_rejects_a_fact_path_the_selected_source_cannot_supply(copied_rules: Path) -> None:
    rule_path = copied_rules / "school-access-rules.yaml"
    rule_path.write_text(
        rule_path.read_text(encoding="utf-8").replace(
            "              - ref: requirements.validity_restriction_accepted",
            "              - fact: qualification.teaching_hours\n                gte: 400",
            1,
        )
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "INVALID_FACT_PATH"


def test_activation_rejects_a_value_outside_the_fact_domain(copied_rules: Path) -> None:
    rule_path = copied_rules / "school-access-rules.yaml"
    rule_path.write_text(
        rule_path.read_text(encoding="utf-8").replace(
            "eq: ALLGEMEINE_HOCHSCHULREIFE", "eq: ALLGEMEINE_HOCHSCHULEREIFE", 1
        )
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "UNKNOWN_FACT_VALUE"


def test_activation_rejects_a_reason_code_with_no_configured_explanation(copied_rules: Path) -> None:
    rule_path = copied_rules / "school-access-rules.yaml"
    rule_path.write_text(
        rule_path.read_text(encoding="utf-8").replace(
            "GERMAN_ABITUR_DIRECT_ACCESS", "GERMAN_ABITUR_DIRECT_ACESS", 1
        )
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "UNKNOWN_REASON_CODE"


def test_activation_rejects_a_threshold_that_is_not_an_integer(copied_rules: Path) -> None:
    """A boolean threshold must not be coerced into `>= 1`."""
    requirements_path = copied_rules / "common" / "requirements.yaml"
    requirements_path.write_text(
        requirements_path.read_text(encoding="utf-8").replace("gte: 400", "gte: true", 1)
    )

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "INVALID_REFERENCE_TARGET"


def test_activation_reports_malformed_yaml_as_a_typed_activation_error(copied_rules: Path) -> None:
    requirements_path = copied_rules / "common" / "requirements.yaml"
    requirements_path.write_text('dsl_version: "1.3"\nmodule:\n  id: BROKEN\n   bad: indent\n')

    with pytest.raises(PolicyActivationError) as raised:
        RulesEngine.activate(copied_rules)

    assert raised.value.code == "INVALID_POLICY_YAML"


def test_every_compiler_fact_path_is_supplied_by_its_candidate_collection(rules_root: Path) -> None:
    """Keep the compiler fact table and the evaluator candidate builder from drifting apart."""
    from app.models.artifacts import ApplicationFactsArtifact
    from app.rules_engine.compiler import _SOURCE_FACTS
    from app.rules_engine.evaluator import _build_candidates

    del rules_root
    from scenario_support import make_artifact

    artifact: ApplicationFactsArtifact = make_artifact(
        {"id": "drift", "school": {}, "advanced": {}, "professional": {}}
    )
    candidates = _build_candidates(artifact)

    for source, facts in _SOURCE_FACTS.items():
        built = candidates[source]
        assert built, f"{source} produced no candidate to compare against"
        assert set(facts) == set(built[0].facts), f"{source} fact paths drifted from the compiler table"
