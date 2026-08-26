"""Reconstruct every intermediate state of compiles and runs from persisted outputs.

Nothing is re-run and no tokens are spent: the compile nav traces come from
runs/criteria/{arm}.json, and each graph node's output comes from the raw API
responses in runs/raw/ (keyed {run_id}--{node}.json).

CLI:  uv run python -m src.walkthrough   ->  prints and writes runs/walkthrough.md
"""

import json

from . import config
from .run import load_records

NODE_ORDER = ["evaluator_t1", "critic_lookup", "critic_review_t1", "evaluator_t2", "critic_review_t2"]


def parsed_output(run_id: str, node: str) -> dict | None:
    """The structured output of one node, recovered from its raw response file."""
    path = config.RAW_DIR / f"{run_id}--{node}.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    texts = [c.get("text") for item in raw.get("output", []) if item.get("type") == "message"
             for c in item.get("content", []) if c.get("type") == "output_text"]
    return json.loads(texts[-1]) if texts else None


def _decision_lines(d: dict, indent: str = "") -> list[str]:
    lines = [f"{indent}- status: **{d['application_status']}**",
             f"{indent}- rationale: {d['rationale']}"]
    for key in ("conditions", "missing_information", "manual_review_reasons"):
        if d.get(key):
            lines.append(f"{indent}- {key}: {d[key]}")
    lines.append(f"{indent}- assessments:")
    for a in d.get("criteria_assessments", []):
        lines.append(f"{indent}  - `{a['verdict']}` {a['criterion_id']}: {a['reasoning']}")
        if a.get("evidence"):
            lines.append(f"{indent}    - evidence: {a['evidence']}")
    return lines


def compile_walkthrough() -> list[str]:
    lines = ["# Walkthrough — every intermediate state", "", "## Compile step (once per arm)", ""]
    for arm in config.ARMS:
        path = config.CRITERIA_DIR / f"{arm}.json"
        lines.append(f"### ARM_{arm.upper()}")
        if not path.exists():
            lines += ["", "not compiled yet", ""]
            continue
        artifact = json.loads(path.read_text())
        lines += ["", f"coverage_complete={artifact['coverage_complete']}, "
                      f"{len(artifact['opened_section_ids'])} sections opened, "
                      f"{len(artifact['criteria']['criteria'])} criteria compiled", ""]
        for turn in artifact["nav_trace"]:
            lines += [f"**Nav turn {turn['turn']}** — {turn['rationale']}",
                      f"- requested: {turn['requested']}",
                      f"- retrieved: {turn['retrieved_titles']}",
                      f"- coverage_complete: {turn['coverage_complete']}", ""]
        lines.append("**Compiled criteria:**")
        for c in artifact["criteria"]["criteria"]:
            lines.append(f"- `{c['criterion_id']}` ({', '.join(c['citations'])}): {c['summary']}")
        lines.append("")
    return lines


def rules_walkthrough(persona: str) -> list[str]:
    """The rule-based system's verdict for this persona, from baseline/<persona>/."""
    d = config.BASELINE_DIR / persona
    result, failure = d / "application-result.json", d / "processing-failure.json"
    lines = [f"## {persona} — rules engine (baseline)", ""]
    if result.exists():
        j = json.loads(result.read_text())
        lines += [f"final: **{j['application_status']}** (`{j['application_reason_code']}`)",
                  f"- headline: {j['summary']['canonical']['headline']}"]
        if j.get("missing_information"):
            lines.append(f"- missing: {[m['label'] for m in j['missing_information']]}")
        if j.get("manual_review"):
            lines.append(f"- manual review: {[m['reason_code'] for m in j['manual_review']]}")
        lines.append("")
    elif failure.exists():
        j = json.loads(failure.read_text())
        lines += [f"final: **RUN_FAILED** (`{j.get('code', 'UNKNOWN')}`) — {j.get('safe_message', '')}", ""]
    else:
        lines += ["not run yet", ""]
    return lines


def run_walkthrough(record: dict) -> list[str]:
    run_id, persona, arm = record["run_id"], record["persona"], record["arm"]
    critic = record["critic"]
    lines = [f"## {persona} — ARM_{arm.upper()} (repeat {record['repeat']}, `{run_id}`)", "",
             f"final: **{record['application_status']}** · critic: "
             + ("approved first pass" if critic["approved_first"]
                else f"retried, {'resolved' if critic['resolved'] else 'UNRESOLVED'}"
                     + f" (status before retry: {critic['status_before_retry']})"), ""]

    evaluator = parsed_output(run_id, "evaluator_t1")
    if evaluator:
        lines += ["### 1 · evaluator (draft decision)"] + _decision_lines(evaluator) + [""]

    lookup = parsed_output(run_id, "critic_lookup")
    if lookup:
        requested = lookup.get("open_section_ids", lookup.get("search_queries", []))
        lines += ["### 2 · critic lookup",
                  f"- rationale: {lookup['rationale']}",
                  f"- requested: {requested}", ""]

    review1 = parsed_output(run_id, "critic_review_t1")
    if review1:
        lines += ["### 3 · critic review", f"- approve: **{review1['approve']}**"]
        if review1.get("objection"):
            lines += [f"- objection: {review1['objection']}",
                      f"- policy evidence: {review1['policy_evidence']}"]
        lines.append("")

    retry = parsed_output(run_id, "evaluator_t2")
    if retry:
        lines += ["### 4 · evaluator retry (after objection)"] + _decision_lines(retry) + [""]

    review2 = parsed_output(run_id, "critic_review_t2")
    if review2:
        lines += ["### 5 · critic review of the retry", f"- approve: **{review2['approve']}**"]
        if review2.get("objection"):
            lines += [f"- objection: {review2['objection']}"]
        lines.append("")
    return lines


def main() -> None:
    lines = compile_walkthrough()
    lines += ["---", "", "# Applicant runs", ""]
    records = sorted(load_records().values(), key=lambda r: (r["persona"], r["arm"], r["repeat"]))
    seen_personas = set()
    for record in records:
        if record["persona"] not in seen_personas:
            seen_personas.add(record["persona"])
            lines += rules_walkthrough(record["persona"]) + ["---", ""]
        lines += run_walkthrough(record) + ["---", ""]
    out = config.RUNS_DIR / "walkthrough.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
