# Spec: Agentic RAG admissions prototype (`experiment/admissions-agentic-rag`)

Status: ready-for-agent
Scope: POC — prove the point, cover major branches, no production hardening.

## Problem Statement

The full policy workflow prototype (`alternate-options/option-b-full-policy-workflow`) showed
that a straight LLM pipeline over the full policy document is worse than the rule-based
system on every axis that matters: lower core accuracy (44% vs 67%), a 44% flip-rate
across repeats (vs 0 by construction), and ~7.6× the input tokens per applicant because
the 93.5k-token Leitfaden is re-read on every run. Its dominant failure was calibration
(defaulting to MISSING_INFORMATION, never INELIGIBLE, one unstable false ELIGIBLE).

The open question: can an _agentic_ architecture — not a compiled rules engine — get
meaningfully closer to the rule-based system's reliability and cost if we (1) stop
re-reading the policy per applicant, (2) give the policy analyst bounded agentic
retrieval loops instead of one blind full-document pass, and (3) add a critic that can
verify verdicts against retrieved policy text and demand one retry?

## Solution

A third prototype: an Agentic RAG screener where policy criteria are **compiled once
per retrieval arm** by a policy analyst with bounded navigation loops, cached on disk,
and reused for every applicant. Each applicant run is a LangGraph of
evaluator → critic → (optional single retry) → final verdict. Two retrieval arms are
compared end-to-end — **ARM_TOC** (chunkless heading-index navigation, sections opened
by ID) and **ARM_RAG** (Chroma vector store over the same section inventory,
`text-embedding-3-small`, query → top-k=4). A three-way evaluation compares this
prototype against the rule-based system (fresh baseline rerun) and the full policy
workflow's existing 48 runs, on accuracy vs. eval-tuple labels, agreement, flip-rate,
cost/tokens, and critic effectiveness — plus a compile-time retrieval-quality table
against the rule-extractor's navigation-trace ground truth.

## User Stories

1. As the case-study author, I want a compile-once criteria step, so that per-applicant runs stop paying the 93.5k-token policy re-read.
2. As the case-study author, I want the criteria artifact cached and keyed on policy + instructions hashes, so that reruns are free and recompiles happen automatically when inputs change.
3. As the case-study author, I want the policy analyst to navigate the document over bounded agentic loops (≤3 turns), so that criteria derivation is grounded in retrieved sections rather than one blind pass.
4. As the case-study author, I want a `coverage_complete` flag persisted when the loop bound is hit, so that degraded compiles are recorded instead of hidden.
5. As the case-study author, I want two retrieval arms (TOC navigation vs. Chroma semantic search) over the _same_ section inventory, so that the comparison isolates the selection mechanism as the only variable.
6. As the case-study author, I want the evaluator to receive the cached criteria plus all of the applicant's PDFs (scanned variants included — constraint removed after review), so that each applicant run is cheap and self-contained.
7. As the case-study author, I want a critic that reviews the verdict, assessments, and cited evidence — with its arm's retrieval tool to open policy text — so that calibration errors get caught before the verdict is final.
8. As the case-study author, I want the critic limited to APPROVE or one RETRY (with its objection and retrieved policy text attached), so that the loop is bounded and the critic never becomes a second evaluator.
9. As the case-study author, I want unresolved disagreement after the retry to keep the evaluator's last verdict but set `critic_unresolved: true`, so that the accuracy metric stays uncontaminated and critic noise is measurable.
10. As the case-study author, I want every LLM call ledgered (tokens, duration, instruction hashes) with raw responses persisted, so that cost and behavior claims in the writeup are backed by data.
11. As the case-study author, I want LangSmith tracing in a dedicated project, so that traces don't interleave with the full policy workflow's.
12. As the case-study author, I want a 16-persona × 3-repeat × 2-arm batch runner that is idempotent and parallel, so that interrupted runs resume without re-spending tokens.
13. As the case-study author, I want the batch gated behind an explicit go signal, so that no API spend happens before I approve it.
14. As the case-study author, I want a three-way evaluation (rules vs. full policy workflow vs. this prototype, per arm), so that the writeup can rank all three architectures on the same labels.
15. As the case-study author, I want flip-rate computed over the 3 repeats, so that stability is compared like-for-like with the earlier experiments.
16. As the case-study author, I want a critic-effectiveness report (caught / resolved / contested counts, verdicts changed by retry), so that the critic's value is measured, not assumed.
17. As the case-study author, I want a compile-time retrieval-quality table (sections each arm opened vs. the rule-extractor navigation-trace ground truth), so that retrieval precision/recall is reported per arm.
18. As the case-study author, I want a small reviewable folder structure with one module per concern, so that the POC is easy to walk through in review.
19. As a reviewer, I want the README to state the thesis, the fairness rules, and the stated limitations (e.g. section-level chunking), so that the experiment's claims are scoped honestly.
20. As the case-study author, I want the rule-based baseline rerun fresh (16 personas, digital PDFs only) while the full policy workflow's existing results are reused, so that comparison cost stays proportionate.

## Implementation Decisions

- Standalone uv project; zero imports from `app/` (clean-room rule carried over). EXPECTED labels copied in as data.
- Model `gpt-5.6-terra` everywhere (fairness); OpenAI Responses API with pydantic structured outputs, `store=False`; applicant PDFs as base64 `input_file` data URIs. All PDFs are sent, scanned variants included (the digital-only filter was removed by decision after the quick run).
- LangGraph StateGraph per applicant: `evaluator → critic → conditional(retry evaluator once | end)`. Compile step is _not_ in the per-applicant graph — it runs at a different cadence and that separation is the architectural point.
- Section inventory (hierarchical, decided after the quick run): regex over `##`/`###` headings of the English Leitfaden markdown; `###` sections carry their parent `##` chapter title as a breadcrumb (in the TOC, the embedded docs, and retrieval renders); childless `##` chapters are sections with their content; heading-only `##` shells are dropped from the inventory and survive only as breadcrumbs. IDs number ALL headings in document order, so they stay stable. Both arms retrieve from this inventory.
- ARM_TOC tool: agent sees compact TOC, returns `NavigationTurn{rationale, open_section_ids, coverage_complete}`; harness returns full section text; ≤3 turns.
- ARM_RAG tool: agent emits a search query per turn; Chroma collection (persisted under `runs/`) over the inventory with `text-embedding-3-small`; top-k=4 returned; same turn budget. Multi-vector embedding: sections with `####` sub-headings get one vector per sub-block (ids like `s004#2`), `#####` variants staying inside their parent block; hits always resolve to whole sections, so the retrieval unit is unchanged. Collection name carries policy sha + `INDEX_SCHEMA` version; `INDEX_SCHEMA` is also folded into the criteria-cache instructions hash so retrieval-scheme changes recompile. Chroma chosen over FAISS for built-in collection management + OpenAI embedding integration.
- Criteria artifact per arm: criteria list with section citations, `coverage_complete`, policy sha256, instructions sha256, arm id, compile ledger refs. Cache hit = all hashes match; miss = recompile.
- Critic inputs: verdict + criteria assessments + evaluator evidence quotes (not raw PDFs). Actions: APPROVE | RETRY(objection, retrieved policy text). Max 1 retry; terminal disagreement → keep last verdict + `critic_unresolved: true`.
- Shared 5-value ApplicationStatus vocabulary (ELIGIBLE / CONDITIONALLY_ELIGIBLE / INELIGIBLE / MISSING_INFORMATION / MANUAL_REVIEW); RuleId taxonomy withheld (fairness, same as prototype 1).
- Observability: `runs/ledger.jsonl` (thread-safe append; tokens, duration, sha256 of instructions) + `runs/raw/` full responses + LangSmith `wrap_openai`, project `auto-admissions-agentic-rag` (EU endpoint from repo `.env`).
- Batch: ThreadPoolExecutor, idempotent cache keyed on (persona, repeat, arm), results appended to `runs/results.jsonl`.
- Eval outputs: `runs/eval-summary.json`, `runs/comparison.csv`, `runs/disagreements.md`, `runs/cost-summary.json`, `runs/retrieval-quality.md` — same shapes as prototype 1 where they overlap, extended with arm and critic columns.
- Rerun scope: `baseline.sh` pattern reused for a fresh rules baseline into this project's `baseline/`; full policy workflow results read read-only from its existing `runs/` files.
- Folder shape: `src/config.py`, `src/models.py`, `src/observability.py`, `src/policy_index.py` (inventory + both retrieval tools), `src/prompts/` (LLM prompt constants), `src/compile_policy.py`, `src/graph.py` (evaluator + critic nodes + graph), `src/run.py`, `src/evaluate.py`.

## Testing Decisions

- POC: no full test pyramid. Two seams:
  1. **Highest seam (behavioral):** the CLI entrypoints — `python -m src.compile_policy`, `python -m src.run`, `python -m src.evaluate` — verified by their persisted outputs (criteria artifacts, results.jsonl, eval files). API-spending verification is the gated batch itself.
  2. **Pure-code seam (pytest, no LLM):** `policy_index` heading parse + section fetch on the real Leitfaden (section count, span integrity, lookup by ID), criteria-cache keying (hash match/miss), and eval math (modal verdict, flip-rate, accuracy) on fixture records.
- Good test = asserts external behavior (parsed sections, cache decisions, computed metrics), never prompt strings or internal call order.
- Prior art: prototype 1 verified via executed notebook + persisted `runs/` outputs; the rules repo has pytest suites for deterministic logic.

## Out of Scope

- Production hardening: retries/backoff policy tuning, auth, deployment, scanned-PDF OCR path.
- Tool-using evaluator agents (documented business option in root TDD, D5-B).
- Paragraph-level chunking for ARM_RAG (`####` sub-block vectors were added by decision after the quick run; anything finer stays out).
- Embedding-model comparison; third retrieval arms.
- Changes to `app/`, the rules engine, or the full policy workflow.
- Master's policy — bachelor academic entrance qualification only, same scope as prior experiments.

## Further Notes

- Retrieval ground truth: `rule-extractor/artifacts/navigation-trace.json` (bachelor run) — 10 sections opened, coverage in one turn.
- The Leitfaden markdown has ~142 `##`/`###` headings; inventory granularity mirrors the rule-extractor's (chapter-level `##` with `###` subsections attached to their parent where needed).
- Thesis to test, stated in README: "reliability and cost pressure push an agentic design toward compiled policy + cheap per-applicant evaluation — i.e. toward the rule-based architecture — but the critic + retrieval loop may close part of the calibration gap without a DSL."
- No batch/API run starts without the user's explicit go signal.
