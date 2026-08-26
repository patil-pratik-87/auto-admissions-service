"""Compile-once policy step: bounded agentic navigation -> cached criteria artifact.

This runs at a different cadence than the per-applicant graph — once per retrieval
arm, not once per applicant. That separation is the architectural point of the
experiment: the 93.5k-token policy read is paid once and amortized to ~zero.

Cache contract: `runs/criteria/{arm}.json` is valid while the policy file hash,
the compile-instructions hash, and the arm all match. Any mismatch recompiles.

CLI:  uv run python -m src.compile_policy [--arm toc|rag|both] [--force]
"""

import argparse
import json
import re
import uuid
from datetime import datetime, timezone

from . import config
from .observability import call_agent, sha256_text
from .policy_index import PolicyIndex, RagStore
from .models import CriteriaArtifact, PolicyCriteria, RagNavigationTurn, TocNavigationTurn
from .prompts import (
    COMPILE_TASK,
    EXTRACT_INSTRUCTIONS,
    NAV_RAG_INSTRUCTIONS,
    NAV_TOC_INSTRUCTIONS,
    RAG_SEED_QUERY,
)


def instructions_sha(arm: str) -> str:
    # INDEX_SCHEMA (and, for rag, the seed query and top-k) is folded in so
    # retrieval-scheme changes (which alter what the analyst sees without touching
    # any prompt) also invalidate the criteria cache. RAG_FOLLOWUP_TURNS needs no
    # folding: it appears verbatim in NAV_RAG_INSTRUCTIONS.
    nav = NAV_TOC_INSTRUCTIONS if arm == "toc" else f"{NAV_RAG_INSTRUCTIONS}{RAG_SEED_QUERY} top_k={config.TOP_K}"
    return sha256_text(COMPILE_TASK + nav + EXTRACT_INSTRUCTIONS + config.INDEX_SCHEMA)


def cache_valid(artifact: dict, *, policy_sha256: str, instructions_sha256: str, arm: str) -> bool:
    """Pure cache-key check; the seam the cache tests exercise."""
    return (
        artifact.get("arm") == arm
        and artifact.get("policy_sha256") == policy_sha256
        and artifact.get("instructions_sha256") == instructions_sha256
    )


def artifact_path(arm: str):
    return config.CRITERIA_DIR / f"{arm}.json"


def load_cached(arm: str, index: PolicyIndex) -> CriteriaArtifact | None:
    path = artifact_path(arm)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if not cache_valid(data, policy_sha256=index.sha, instructions_sha256=instructions_sha(arm), arm=arm):
        return None
    return CriteriaArtifact.model_validate(data)


# PDF-conversion page markers (*PAGE 21 OF 245*) land mid-sentence in the markdown;
# a faithful quote skips them, so they must not count as a mismatch.
_PAGE_MARKER_RE = re.compile(r"\*page \d+ of \d+\*", re.IGNORECASE)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", _PAGE_MARKER_RE.sub(" ", text)).casefold().strip()


def unverified_excerpts(index: PolicyIndex, criteria: PolicyCriteria) -> list[str]:
    """criterion_ids with an excerpt that is not a verbatim quote of a cited section.

    Whitespace/case-normalized substring check. A mismatch is a hallucination flag
    recorded on the artifact, never a crash (same philosophy as unresolved IDs).
    """
    flagged = []
    for criterion in criteria.criteria:
        sections, _ = index.fetch(criterion.citations)
        texts = [_normalize(index.text_of(s)) for s in sections]
        if any(not any(_normalize(excerpt) in t for t in texts) for excerpt in criterion.source_excerpts):
            flagged.append(criterion.criterion_id)
    return flagged


def _navigate(arm: str, index: PolicyIndex, run_id: str) -> tuple[dict, list[dict], bool]:
    """The bounded agentic loop. Returns (opened {id: Section}, trace, coverage_complete).

    ARM_RAG starts from a deterministic program-seeded fetch (trace turn 0, no LLM);
    the LLM then gets RAG_FOLLOWUP_TURNS turns to append what is still missing.
    """
    rag_store = RagStore(index) if arm == "rag" else None
    opened: dict[str, object] = {}
    trace: list[dict] = []
    coverage_complete = False
    turn_budget = config.MAX_NAV_TURNS if arm == "toc" else config.RAG_FOLLOWUP_TURNS

    if arm == "rag":
        seed_sections = rag_store.query([RAG_SEED_QUERY], run_id=run_id)
        for s in seed_sections:
            opened[s.section_id] = s
        trace.append({
            "turn": 0,
            "rationale": "Deterministic program-seeded fetch (no LLM).",
            "requested": [RAG_SEED_QUERY],
            "unresolved": [],
            "retrieved_section_ids": [s.section_id for s in seed_sections],
            "retrieved_titles": [s.title for s in seed_sections],
            "coverage_complete": False,
        })

    for turn in range(1, turn_budget + 1):
        opened_block = (
            "Sections already opened:\n\n" + index.render(list(opened.values()))
            if opened else "No sections opened yet."
        )
        if arm == "toc":
            content = [{"type": "input_text", "text": f"{COMPILE_TASK}\n\nTable of contents:\n{index.toc()}\n\n{opened_block}\n\nTurn {turn} of {turn_budget}."}]
            nav = call_agent(node=f"compile_nav_t{turn}", run_id=run_id, instructions=NAV_TOC_INSTRUCTIONS,
                             content=content, schema=TocNavigationTurn, extra={"arm": arm})
            sections, missing = index.fetch(nav.open_section_ids)
            requested = nav.open_section_ids
        else:
            content = [{"type": "input_text", "text": f"{COMPILE_TASK}\n\n{opened_block}\n\nTurn {turn} of {turn_budget}."}]
            nav = call_agent(node=f"compile_nav_t{turn}", run_id=run_id, instructions=NAV_RAG_INSTRUCTIONS,
                             content=content, schema=RagNavigationTurn, extra={"arm": arm})
            sections = rag_store.query(nav.search_queries, run_id=run_id)
            requested, missing = nav.search_queries, []

        for s in sections:
            opened[s.section_id] = s
        trace.append({
            "turn": turn,
            "rationale": nav.rationale,
            "requested": requested,
            "unresolved": missing,
            "retrieved_section_ids": [s.section_id for s in sections],
            "retrieved_titles": [s.title for s in sections],
            "coverage_complete": nav.coverage_complete,
        })
        if nav.coverage_complete:
            coverage_complete = True
            break

    return opened, trace, coverage_complete


def compile_arm(arm: str, *, force: bool = False) -> CriteriaArtifact:
    assert arm in config.ARMS, arm
    index = PolicyIndex.from_file()
    if not force:
        cached = load_cached(arm, index)
        if cached is not None:
            print(f"[{arm}] criteria cache hit ({artifact_path(arm).name})")
            return cached

    run_id = f"compile-{arm}-{uuid.uuid4().hex[:8]}"
    print(f"[{arm}] compiling criteria (run {run_id}) ...")
    opened, trace, coverage_complete = _navigate(arm, index, run_id)
    sections = sorted(opened.values(), key=lambda s: s.start)

    criteria = call_agent(
        node="compile_extract",
        run_id=run_id,
        instructions=EXTRACT_INSTRUCTIONS,
        content=[{"type": "input_text", "text": "Retrieved handbook sections:\n\n" + index.render(sections)}],
        schema=PolicyCriteria,
        extra={"arm": arm},
    )

    unverified = unverified_excerpts(index, criteria)
    artifact = CriteriaArtifact(
        arm=arm,
        model=config.MODEL,
        policy_sha256=index.sha,
        instructions_sha256=instructions_sha(arm),
        compiled_at=datetime.now(timezone.utc).isoformat(),
        coverage_complete=coverage_complete,
        unverified_excerpts=unverified,
        opened_section_ids=[s.section_id for s in sections],
        opened_section_titles=[s.title for s in sections],
        nav_trace=trace,
        criteria=criteria,
    )
    config.CRITERIA_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path(arm).write_text(artifact.model_dump_json(indent=2))
    print(f"[{arm}] {len(criteria.criteria)} criteria from {len(sections)} sections "
          f"(coverage_complete={coverage_complete}, unverified_excerpts={unverified or 'none'}) -> {artifact_path(arm)}")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=[*config.ARMS, "both"], default="both")
    parser.add_argument("--force", action="store_true", help="recompile even on cache hit")
    args = parser.parse_args()
    arms = config.ARMS if args.arm == "both" else (args.arm,)
    for arm in arms:
        compile_arm(arm, force=args.force)


if __name__ == "__main__":
    main()
