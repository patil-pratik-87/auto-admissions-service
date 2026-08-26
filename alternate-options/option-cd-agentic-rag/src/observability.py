"""Observability: LangSmith-wrapped client, run ledger, raw response persistence.

Three layers, all cheap (same stance as the earlier experiments):
1. LangSmith tracing — the OpenAI client is wrapped with `wrap_openai`, project set by
   AGENTIC_RAG_LANGSMITH_PROJECT (default `auto-admissions-agentic-rag`; EU endpoint from the repo .env).
2. Run ledger — `runs/ledger.jsonl`, one line per model call: node, arm, tokens,
   latency, instruction hash. The cost comparison reads this.
3. Raw responses — every full API response under `runs/raw/`, so any disagreement
   can be audited without re-running anything.
"""

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config

_JSONL_LOCK = threading.Lock()  # batch runs append from worker threads
_client = None


def get_client():
    global _client
    if _client is None:
        assert os.environ.get("OPENAI_API_KEY"), "OPENAI_API_KEY missing - check the repo root .env"
        from langsmith.wrappers import wrap_openai
        from openai import OpenAI

        _client = wrap_openai(OpenAI(max_retries=2))
    return _client


def append_jsonl(path: Path, record: dict) -> None:
    with _JSONL_LOCK:
        with path.open("a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def call_agent(*, node: str, run_id: str, instructions: str, content: list, schema, extra: dict | None = None,
               model: str | None = None):
    """One structured-output model call, fully observed.

    Returns the parsed pydantic object; raises if the model returned no parseable
    output (refusal / truncation) so a failed call is never silently treated as data.
    """
    model = model or config.MODEL
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    response = get_client().responses.parse(
        model=model,
        instructions=instructions,
        input=[{"role": "user", "content": content}],
        text_format=schema,
        max_output_tokens=config.MAX_OUTPUT_TOKENS,
        store=False,
    )
    duration_ms = round((time.perf_counter() - started) * 1000)

    raw_path = config.RAW_DIR / f"{run_id}--{node}.json"
    raw_path.write_text(response.model_dump_json(indent=2))
    usage = response.usage
    append_jsonl(config.LEDGER_PATH, {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "node": node,
        "model": model,
        "status": response.status,
        "input_tokens": usage.input_tokens if usage else None,
        "output_tokens": usage.output_tokens if usage else None,
        "duration_ms": duration_ms,
        "instructions_sha256": sha256_text(instructions)[:16],
        "raw": str(raw_path.relative_to(config.EXPERIMENT_DIR)),
        **(extra or {}),
    })

    if response.output_parsed is None:
        raise RuntimeError(f"{node} produced no parsed output (status={response.status}) - see {raw_path}")
    return response.output_parsed


def embed_texts(texts: list[str], *, run_id: str, node: str = "embed") -> list[list[float]]:
    """Embed texts for ARM_RAG; ledgered like every other API call (embeddings have no raw file)."""
    started = time.perf_counter()
    response = get_client().embeddings.create(model=config.EMBED_MODEL, input=texts)
    append_jsonl(config.LEDGER_PATH, {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "node": node,
        "model": config.EMBED_MODEL,
        "status": "completed",
        "input_tokens": response.usage.total_tokens if response.usage else None,
        "output_tokens": 0,
        "duration_ms": round((time.perf_counter() - started) * 1000),
        "n_texts": len(texts),
    })
    return [d.embedding for d in response.data]
