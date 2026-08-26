from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

RULES_ROOT = Path(__file__).parents[2] / "rules"


def _walk(value: Any) -> Iterator[Any]:
    yield value
    if isinstance(value, Mapping):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, Sequence) and not isinstance(value, str):
        for child in value:
            yield from _walk(child)


def test_authored_rules_use_the_deterministic_dsl_shape() -> None:
    """The active policy must not retain legacy semantic or queue behavior."""
    yaml = YAML(typ="safe")
    documents = [yaml.load(path) for path in sorted(RULES_ROOT.rglob("*.yaml"))]

    assert {document["dsl_version"] for document in documents} == {"1.3"}
    policy = next(document["policy"] for document in documents if "policy" in document)
    assert policy["version"] == "0.0.22"

    all_values = tuple(value for document in documents for value in _walk(document))
    mappings = tuple(value for value in all_values if isinstance(value, Mapping))
    strings = tuple(value for value in all_values if isinstance(value, str))
    branch_groups = tuple(mapping["branches"] for mapping in mappings if "branches" in mapping)
    legacy_term = "rou" + "te"

    assert all("evaluate" not in mapping for mapping in mappings)
    assert all("queue" not in mapping for mapping in mappings)
    assert all("priority" not in mapping for mapping in mappings)
    assert all("scope" not in mapping for mapping in mappings)
    assert all(legacy_term not in str(key).lower() for mapping in mappings for key in mapping)
    assert all(legacy_term not in value.lower() for value in strings)
    assert all(not value.startswith("$") for value in strings)
    assert strings.count("requirements.german_qualification") == 3
    assert (
        sum(mapping.get("fact") == "qualification.country" and mapping.get("eq") == "DE" for mapping in mappings) == 1
    )
    assert branch_groups
    assert all(set(group) == {"first_match", "unknown", "otherwise"} for group in branch_groups)
