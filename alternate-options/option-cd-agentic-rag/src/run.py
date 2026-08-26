"""Batch runner: personas x repeats x arms, parallel and idempotent.

Completed (persona, repeat, arm) runs are cached in runs/results.jsonl and never
re-run, so interrupting and re-invoking is safe and free. Criteria are loaded from
the compile cache (compiled on demand if absent).

CLI:  uv run python -m src.run [--arm toc|rag|both] [--personas a b c]
                               [--repeats N] [--workers N] [--force]
NOTE: this spends API tokens — run only on an explicit go.
"""

import argparse
import json
import uuid
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .compile_policy import compile_arm
from .graph import build_graph
from .observability import append_jsonl
from .policy_index import PolicyIndex


def applicant_pdfs(persona: str) -> list[Path]:
    """Every PDF the persona uploaded, scanned variants included."""
    folder = config.SAMPLES_DIR / persona
    return sorted(folder.glob("*.pdf"))


def load_records(path: Path = config.RESULTS_PATH) -> dict:
    """All persisted run records, keyed by (persona, repeat, arm)."""
    records = {}
    if path.exists():
        for line in path.open():
            r = json.loads(line)
            records[(r["persona"], r["repeat"], r["arm"])] = r
    return records


def run_applicant(graph, artifact, arm: str, persona: str, repeat: int) -> dict:
    run_id = f"{arm}-{persona}-r{repeat}-{uuid.uuid4().hex[:8]}"
    pdfs = applicant_pdfs(persona)
    assert pdfs, f"no PDFs for {persona}"
    state = graph.invoke(
        {"persona": persona, "run_id": run_id, "repeat": repeat, "arm": arm,
         "pdf_paths": pdfs, "artifact": artifact},
        config={"run_name": run_id},
    )
    final = state["final_decision"]
    outcome = state["critic_outcome"]
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "persona": persona,
        "repeat": repeat,
        "arm": arm,
        "model": config.MODEL,
        "pdfs": [p.name for p in pdfs],
        "application_status": final.application_status,
        "critic": outcome.model_dump(),
        "decision": final.model_dump(),
    }
    append_jsonl(config.RESULTS_PATH, record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=[*config.ARMS, "both"], default="both")
    parser.add_argument("--personas", nargs="*", default=None)
    parser.add_argument("--repeats", type=int, default=config.N_REPEATS)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true", help="re-run even if a record exists")
    args = parser.parse_args()

    arms = config.ARMS if args.arm == "both" else (args.arm,)
    personas = args.personas or sorted(p.name for p in config.SAMPLES_DIR.iterdir() if p.is_dir())

    index = PolicyIndex.from_file()
    graphs = {arm: (build_graph(index, arm), compile_arm(arm)) for arm in arms}

    done = {} if args.force else load_records()
    pending = [(arm, p, r)
               for arm in arms for r in range(args.repeats) for p in personas
               if (p, r, arm) not in done]
    print(f"{len(personas)} personas x {args.repeats} repeats x {len(arms)} arm(s): "
          f"{len(done)} cached, {len(pending)} pending")
    if not pending:
        return

    failures, completed = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}

        def submit_next():
            if pending:
                arm, p, r = pending.pop(0)
                graph, artifact = graphs[arm]
                futures[pool.submit(run_applicant, graph, artifact, arm, p, r)] = (arm, p, r)

        for _ in range(args.workers):
            submit_next()
        while futures:
            finished, _ = wait(futures, return_when=FIRST_COMPLETED)
            for fut in finished:
                arm, p, r = futures.pop(fut)
                try:
                    rec = fut.result()
                    completed += 1
                    critic = rec["critic"]
                    note = ("approved" if critic["approved_first"]
                            else "resolved" if critic["resolved"] else "UNRESOLVED")
                    print(f"[{arm}] r{r} {p}: {rec['application_status']} (critic {note})")
                except Exception as exc:
                    failures.append((arm, r, p, repr(exc)))
                    print(f"[{arm}] r{r} {p}: FAILED - {exc!r}")
                submit_next()

    print(f"\ncompleted {completed}, failed {len(failures)}")
    for f in failures:
        print("  FAILED:", f)


if __name__ == "__main__":
    main()
