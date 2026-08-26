"""Criteria-cache keying: hash match loads, any mismatch recompiles."""

from src.compile_policy import cache_valid, instructions_sha


ARTIFACT = {"arm": "toc", "policy_sha256": "abc", "instructions_sha256": "def"}


def test_cache_hit_when_all_keys_match():
    assert cache_valid(ARTIFACT, policy_sha256="abc", instructions_sha256="def", arm="toc")


def test_changed_policy_invalidates():
    assert not cache_valid(ARTIFACT, policy_sha256="CHANGED", instructions_sha256="def", arm="toc")


def test_changed_instructions_invalidate():
    assert not cache_valid(ARTIFACT, policy_sha256="abc", instructions_sha256="CHANGED", arm="toc")


def test_other_arm_never_hits():
    assert not cache_valid(ARTIFACT, policy_sha256="abc", instructions_sha256="def", arm="rag")


def test_empty_or_legacy_artifact_never_hits():
    assert not cache_valid({}, policy_sha256="abc", instructions_sha256="def", arm="toc")


def test_arms_have_distinct_instruction_hashes():
    assert instructions_sha("toc") != instructions_sha("rag")
