"""Per-applicant LangGraph: evaluator <-> critic loop, bounded by MAX_CRITIC_RETRIES.

The critic is a reviewer, not a second evaluator: it sees the verdict, the
per-criterion assessments and the evaluator's evidence quotes (NOT the raw PDFs),
opens policy text via its arm's retrieval tool on its first pass, and either
APPROVES or demands a RETRY with its objection and the retrieved policy text
attached. Terminal disagreement keeps the evaluator's last verdict and flags
`critic_unresolved` — the accuracy metric stays uncontaminated, critic noise
stays measurable.

Node names carry the pass number (evaluator_t1, critic_review_t2, ...) so each
pass keeps its own raw response file and ledger identity.
"""

import base64
import json
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from . import config
from .observability import call_agent
from .policy_index import PolicyIndex, RagStore, Section
from .models import (
    AdmissionDecision,
    CriteriaArtifact,
    CriticOutcome,
    CriticReview,
    RagCriticLookup,
    TocCriticLookup,
)
from .prompts import (
    CRITIC_LOOKUP_RAG_INSTRUCTIONS,
    CRITIC_LOOKUP_TOC_INSTRUCTIONS,
    CRITIC_REVIEW_INSTRUCTIONS,
    EVALUATOR_INSTRUCTIONS,
    RETRY_ADDENDUM,
)


class RunState(TypedDict, total=False):
    persona: str
    run_id: str
    repeat: int
    arm: str
    pdf_paths: list[Path]
    artifact: CriteriaArtifact
    decision: AdmissionDecision
    first_decision: AdmissionDecision
    critic_sections_text: str
    reviews: list[CriticReview]
    final_decision: AdmissionDecision
    critic_outcome: CriticOutcome


def _pdf_block(path: Path) -> dict:
    data = base64.b64encode(path.read_bytes()).decode()
    return {"type": "input_file", "filename": path.name,
            "file_data": f"data:application/pdf;base64,{data}"}


def _criteria_block(state: RunState) -> str:
    return (
        f"Program context:\n{json.dumps(config.PROGRAM_CONTEXT, indent=2)}\n\n"
        f"Compiled admission criteria (from the official policy):\n"
        f"{state['artifact'].criteria.model_dump_json(indent=2)}"
    )


def _draft_block(state: RunState) -> str:
    return f"Draft decision under review:\n{state['decision'].model_dump_json(indent=2)}"


def build_graph(index: PolicyIndex, arm: str):
    rag_store = RagStore(index) if arm == "rag" else None

    def evaluator(state: RunState) -> RunState:
        reviews = state.get("reviews", [])
        attempt = len(reviews) + 1
        if reviews:  # retry pass: the last review carries the objection
            review = reviews[-1]
            preamble = (
                f"{_criteria_block(state)}\n\n"
                f"Your previous decision:\n{state['decision'].model_dump_json(indent=2)}\n\n"
                f"Reviewer objection:\n{review.objection}\n\n"
                f"Policy text the reviewer retrieved:\n{review.policy_evidence}\n\n"
                f"Additional policy sections:\n{state['critic_sections_text']}\n\n"
                f"The applicant's documents follow ({len(state['pdf_paths'])} PDFs)."
            )
            instructions = EVALUATOR_INSTRUCTIONS + RETRY_ADDENDUM
        else:
            preamble = f"{_criteria_block(state)}\n\nThe applicant's documents follow ({len(state['pdf_paths'])} PDFs)."
            instructions = EVALUATOR_INSTRUCTIONS
        content = [{"type": "input_text", "text": preamble}]
        content += [_pdf_block(p) for p in state["pdf_paths"]]
        decision = call_agent(node=f"evaluator_t{attempt}", run_id=state["run_id"],
                              instructions=instructions, content=content,
                              schema=AdmissionDecision, extra={"arm": arm, "persona": state["persona"]})
        update: RunState = {"decision": decision, "final_decision": decision}
        if not reviews:
            update["first_decision"] = decision
        return update

    def _lookup(state: RunState) -> str:
        text = f"{_criteria_block(state)}\n\n{_draft_block(state)}"
        if arm == "toc":
            content = [{"type": "input_text", "text": f"{text}\n\nTable of contents:\n{index.toc()}"}]
            lookup = call_agent(node="critic_lookup", run_id=state["run_id"],
                                instructions=CRITIC_LOOKUP_TOC_INSTRUCTIONS, content=content,
                                schema=TocCriticLookup, extra={"arm": arm, "persona": state["persona"]},
                                model=config.CRITIC_MODEL)
            sections: list[Section] = index.fetch(lookup.open_section_ids)[0]
        else:
            content = [{"type": "input_text", "text": text}]
            lookup = call_agent(node="critic_lookup", run_id=state["run_id"],
                                instructions=CRITIC_LOOKUP_RAG_INSTRUCTIONS, content=content,
                                schema=RagCriticLookup, extra={"arm": arm, "persona": state["persona"]},
                                model=config.CRITIC_MODEL)
            sections = rag_store.query(lookup.search_queries, run_id=state["run_id"])
        return index.render(sections) if sections else "(the critic requested no policy text)"

    def critic(state: RunState) -> RunState:
        reviews = state.get("reviews", [])
        attempt = len(reviews) + 1
        # Policy lookup happens once, on the first pass; retry reviews reuse it.
        sections_text = state["critic_sections_text"] if reviews else _lookup(state)
        text = (
            f"{_criteria_block(state)}\n\n{_draft_block(state)}\n\n"
            f"Original policy sections retrieved for verification:\n\n{sections_text}"
        )
        review = call_agent(node=f"critic_review_t{attempt}", run_id=state["run_id"],
                            instructions=CRITIC_REVIEW_INSTRUCTIONS,
                            content=[{"type": "input_text", "text": text}],
                            schema=CriticReview, extra={"arm": arm, "persona": state["persona"]},
                            model=config.CRITIC_MODEL)
        reviews = reviews + [review]
        update: RunState = {"critic_sections_text": sections_text, "reviews": reviews}
        if review.approve or len(reviews) > config.MAX_CRITIC_RETRIES:  # terminal: settle the outcome
            if reviews[0].approve:
                update["critic_outcome"] = CriticOutcome(approved_first=True, retried=False)
            else:
                update["critic_outcome"] = CriticOutcome(
                    approved_first=False,
                    retried=True,
                    resolved=review.approve,
                    critic_unresolved=not review.approve,
                    status_before_retry=state["first_decision"].application_status,
                )
        return update

    def route_after_critic(state: RunState) -> str:
        reviews = state["reviews"]
        if reviews[-1].approve or len(reviews) > config.MAX_CRITIC_RETRIES:
            return "done"
        return "retry"

    builder = StateGraph(RunState)
    builder.add_node("evaluator", evaluator)
    builder.add_node("critic", critic)
    builder.add_edge(START, "evaluator")
    builder.add_edge("evaluator", "critic")
    builder.add_conditional_edges("critic", route_after_critic,
                                  {"done": END, "retry": "evaluator"})
    return builder.compile()
