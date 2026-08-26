"""Verbatim-excerpt verification on a synthetic two-section policy — no LLM, no network."""

from src.compile_policy import unverified_excerpts
from src.models import CompiledCriterion, PolicyCriteria
from src.policy_index import PolicyIndex

DOC = """\
## Route A
Applicants holding an Abitur   qualify
directly for the study program.

## Route B
Completed vocational training of at *PAGE 3 OF 10* least two years qualifies together with an entrance examination.
"""


def criteria_with(*criteria: CompiledCriterion) -> PolicyCriteria:
    return PolicyCriteria(policy_title="t", scope_notes="n", criteria=list(criteria))


def criterion(cid: str, excerpts: list[str], citations: list[str]) -> CompiledCriterion:
    return CompiledCriterion(criterion_id=cid, name="n", summary="s",
                             source_excerpts=excerpts, citations=citations)


def test_verbatim_excerpt_passes_despite_whitespace_and_case():
    idx = PolicyIndex(DOC)  # Route A = s001, Route B = s002
    crit = criterion("abitur", ["applicants holding an Abitur qualify directly"], ["s001"])
    assert unverified_excerpts(idx, criteria_with(crit)) == []


def test_paraphrased_excerpt_is_flagged():
    idx = PolicyIndex(DOC)
    crit = criterion("abitur", ["An Abitur leads to direct qualification."], ["s001"])
    assert unverified_excerpts(idx, criteria_with(crit)) == ["abitur"]


def test_excerpt_from_an_uncited_section_is_flagged():
    idx = PolicyIndex(DOC)
    crit = criterion("vocational", ["Completed vocational training of at least two years"], ["s001"])
    assert unverified_excerpts(idx, criteria_with(crit)) == ["vocational"]


def test_clean_quote_across_a_page_marker_passes():
    idx = PolicyIndex(DOC)  # s002's sentence has *PAGE 3 OF 10* injected mid-sentence
    crit = criterion("vocational", ["Completed vocational training of at least two years qualifies"], ["s002"])
    assert unverified_excerpts(idx, criteria_with(crit)) == []


def test_unknown_citation_is_flagged_not_fatal():
    idx = PolicyIndex(DOC)
    crit = criterion("ghost", ["Applicants holding an Abitur"], ["s999"])
    assert unverified_excerpts(idx, criteria_with(crit)) == ["ghost"]
