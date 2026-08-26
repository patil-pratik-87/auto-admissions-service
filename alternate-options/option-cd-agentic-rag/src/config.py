"""Central configuration: paths, model, bounds, arms.

Reads from the repo root (policy, sample PDFs, .env); writes only inside this
experiment folder. Importing this module must not require an API key.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# --- Locations -----------------------------------------------------------------
EXPERIMENT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = EXPERIMENT_DIR.parent.parent
LEITFADEN_MD = REPO_ROOT / "case-study" / "IU-FS-LF-Leitfaden-Hochschulzugangsberechtigung-Stand-Januar2025.md"


def require_leitfaden() -> Path:
    """The handbook path, checked. Put the English markdown handbook at this path. It is IU material and is not in the repository: see case-study/README.md."""
    if not LEITFADEN_MD.exists():
        raise FileNotFoundError(f"{LEITFADEN_MD}\nPut the English markdown handbook at this path. It is IU material and is not in the repository: see case-study/README.md.")
    return LEITFADEN_MD
SAMPLES_DIR = REPO_ROOT / "samples" / "filled-documents"

# Read-only inputs from the earlier experiments (never written to).
NAIVE_RESULTS_PATH = REPO_ROOT / "alternate-options" / "option-b-full-policy-workflow" / "runs" / "prototype-results.jsonl"
NAIVE_LEDGER_PATH = REPO_ROOT / "alternate-options" / "option-b-full-policy-workflow" / "runs" / "ledger.jsonl"
NAV_TRACE_GROUND_TRUTH = REPO_ROOT / "tools" / "rule-extractor" / "artifacts" / "navigation-trace.json"

RUNS_DIR = EXPERIMENT_DIR / "runs"
RAW_DIR = RUNS_DIR / "raw"
CRITERIA_DIR = RUNS_DIR / "criteria"
CHROMA_DIR = RUNS_DIR / "chroma"
RESULTS_PATH = RUNS_DIR / "results.jsonl"
LEDGER_PATH = RUNS_DIR / "ledger.jsonl"
BASELINE_DIR = EXPERIMENT_DIR / "baseline"  # written by baseline.sh (fresh `admissions screen` runs)

# .env is loaded before the knobs so the env-overridable ones can come from it too.
load_dotenv(REPO_ROOT / ".env")

# --- Experiment knobs ------------------------------------------------------------
# Models. ADMISSIONS_OPENAI_MODEL sets every chat model in the repo at once; these override it.
# Keep this the same as the rule-based system and option B, or the comparison measures two variables.
MODEL = os.getenv("AGENTIC_RAG_MODEL", os.getenv("ADMISSIONS_OPENAI_MODEL", "gpt-5.4-mini"))
CRITIC_MODEL = os.getenv("CRITIC_MODEL", MODEL)
EMBED_MODEL = os.getenv("AGENTIC_RAG_EMBED_MODEL", "text-embedding-3-large")
INDEX_SCHEMA = "hier2-emb3l"       # bump when the inventory/embedding scheme changes:
                                   # invalidates the Chroma collection AND the criteria cache
MAX_OUTPUT_TOKENS = 16_000
MAX_NAV_TURNS = 3                  # ARM_TOC: bounded agentic loop for the policy analyst
RAG_FOLLOWUP_TURNS = int(os.getenv("RAG_FOLLOWUP_TURNS", "2"))  # ARM_RAG: LLM search turns after the program-seeded fetch (0 = seed-only)
MAX_QUERIES_PER_TURN = 3           # ARM_RAG: search queries per navigation turn
TOP_K = int(os.getenv("RAG_TOP_K", "6"))                        # ARM_RAG: sections returned per query
MAX_CRITIC_RETRIES = 1             # critic may demand at most one evaluator retry
N_REPEATS = 3                      # repeats per persona, for the flip-rate metric
ARMS = ("toc", "rag")

# The program the synthetic applicants apply to (mirrors config/programs.yaml: BACHELOR / COMPUTER_SCIENCE).
PROGRAM_CONTEXT = {
    "program": "Bachelor Study Program",
}

# --- Secrets & tracing -----------------------------------------------------------
load_dotenv(REPO_ROOT / ".env")
os.environ["LANGSMITH_PROJECT"] = os.getenv("AGENTIC_RAG_LANGSMITH_PROJECT", "auto-admissions-agentic-rag")
os.environ.setdefault("LANGSMITH_TRACING", "true")
