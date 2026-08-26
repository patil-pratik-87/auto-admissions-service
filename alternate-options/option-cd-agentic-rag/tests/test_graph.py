"""Loop routing and outcome bookkeeping of the evaluator<->critic graph — no LLM, no network.

`call_agent` is monkeypatched; the critic's verdicts are scripted per test. What
is asserted: node names per pass, the retry bound, frozen first_decision, and
the CriticOutcome fields the evaluation reads.
"""

from types import SimpleNamespace

import src.graph as graph_module
from src.graph import build_graph
from src.models import AdmissionDecision, CriticReview, TocCriticLookup
from src.policy_index import PolicyIndex

DOC = """\
## Route A
Applicants holding an Abitur qualify directly.
"""


def decision(status: str) -> AdmissionDecision:
    return AdmissionDecision(application_status=status, rationale="r", conditions=[],
                             missing_information=[], manual_review_reasons=[], criteria_assessments=[])


def fake_state() -> dict:
    artifact = SimpleNamespace(criteria=SimpleNamespace(model_dump_json=lambda **_: "{}"))
    return {"persona": "p", "run_id": "test-run", "repeat": 1, "arm": "toc",
            "pdf_paths": [], "artifact": artifact}


def run_scripted(monkeypatch, *, verdicts: list[bool], statuses: list[str]) -> tuple[dict, list[str]]:
    """Run the toc graph with scripted critic verdicts and evaluator statuses."""
    calls: list[str] = []
    reviews = iter(verdicts)
    decisions = iter(statuses)

    def fake_call_agent(*, node, schema, **_):
        calls.append(node)
        if schema is AdmissionDecision:
            return decision(next(decisions))
        if schema is TocCriticLookup:
            return TocCriticLookup(rationale="check", open_section_ids=["s001"])
        approve = next(reviews)
        return CriticReview(approve=approve, objection="" if approve else "wrong",
                            policy_evidence="" if approve else "Route A")

    monkeypatch.setattr(graph_module, "call_agent", fake_call_agent)
    final = build_graph(PolicyIndex(DOC), "toc").invoke(fake_state())
    return final, calls


def test_first_pass_approval_ends_the_run(monkeypatch):
    final, calls = run_scripted(monkeypatch, verdicts=[True], statuses=["ELIGIBLE"])
    assert calls == ["evaluator_t1", "critic_lookup", "critic_review_t1"]
    assert final["critic_outcome"].approved_first is True
    assert final["critic_outcome"].retried is False
    assert final["final_decision"].application_status == "ELIGIBLE"


def test_rejection_loops_once_then_resolves(monkeypatch):
    final, calls = run_scripted(monkeypatch, verdicts=[False, True],
                                statuses=["ELIGIBLE", "INELIGIBLE"])
    assert calls == ["evaluator_t1", "critic_lookup", "critic_review_t1",
                     "evaluator_t2", "critic_review_t2"]
    outcome = final["critic_outcome"]
    assert (outcome.approved_first, outcome.retried, outcome.resolved) == (False, True, True)
    assert outcome.critic_unresolved is False
    assert outcome.status_before_retry == "ELIGIBLE"
    assert final["first_decision"].application_status == "ELIGIBLE"
    assert final["final_decision"].application_status == "INELIGIBLE"


def test_double_rejection_ends_unresolved_with_last_verdict(monkeypatch):
    final, calls = run_scripted(monkeypatch, verdicts=[False, False],
                                statuses=["ELIGIBLE", "MANUAL_REVIEW"])
    assert calls[-1] == "critic_review_t2"  # MAX_CRITIC_RETRIES=1 -> no third pass
    outcome = final["critic_outcome"]
    assert outcome.critic_unresolved is True
    assert outcome.resolved is False
    assert final["final_decision"].application_status == "MANUAL_REVIEW"
