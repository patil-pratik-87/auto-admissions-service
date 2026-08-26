# Working in this repository

An admissions screening case study. The model reads applicant PDFs and reports facts. Code
decides eligibility. That split is the thesis of the whole design, and three architectures that
put the decision inside a model are kept in `alternate-options/` as the measured counterexample.

Orientation for humans is in [README.md](README.md), and the design reasoning is in
[docs/technical-design-document.md](docs/technical-design-document.md).

## The rules that are not obvious from the code

**The model reports, code decides.** `app/adapters/openai_model.py` returns typed
`ApplicationFacts` and nothing else. Every status comes out of `app/rules_engine/`. A change that
lets a model pick a status breaks D1 in the design document and the accuracy result behind it.

**Four evidence states, three-valued logic.** A fact is `KNOWN`, `MISSING`, `UNREADABLE`, or
`CONFLICTING`, and a condition evaluates to true, false, or unknown. `KNOWN(false)` means the
document said no, and `MISSING` means nobody knows. Keep them apart: `INELIGIBLE` is reachable
only when every applicable rule failed on facts reported as `KNOWN`, so a fact the extractor
missed asks the applicant for a document instead of rejecting them. `app/rules_engine/truth.py`
holds the logic and `test/rules_engine/test_three_valued_logic.py` pins it.

**Documents are identified by content.** `document_id` must equal `sha256:<digest>` of the file
bytes, and `original_filename` is a display label only. Two files with the same name cannot
collide, and the digest is what an audit checks.

**The policy compiles at boot.** `RulesEngine.activate()` in `app/bootstrap.py` eagerly compiles
every YAML file under `rules/`, so a broken package fails at startup and never screens an
applicant. `rules/` must stay a multi-file layout, because the compiler requires it.
`docs/policy-flattened.yaml` is a reading copy for humans and is not loaded by anything.

**Interface models are strict and frozen.** Every Pydantic model uses
`ConfigDict(extra="forbid", frozen=True)`. Adding a field to a saved artifact is a schema version
change, not an edit.

**One retry exists in the system.** The OpenAI client is built with `max_retries=0`, and the
single retry lives inside the facts extractor. Every other failure becomes a
`ProcessingFailureReport` with a typed stage and code, so a broken run is never mistaken for a
decision.

**`store=False` on every model call.** Set in `app/adapters/openai_model.py`,
`evals/judges/openai_judge.py`, and both alternatives. Nothing is retained at the provider.

## Verifying a change

```console
uv run pytest -q          # 98 tests, offline
uv run ruff check app test evals
uv run mypy               # strict, app and evals.judges
```

The suite is offline and stays that way. It calls neither OpenAI nor LangSmith, so a change that
needs a live call needs a fake in `test/`, not a network call.

`test/rules_engine/test_gold_scenarios.py` is the policy gate. It runs 15 scenarios from
`test/fixtures/rules_engine/scenarios.yaml` covering all five rules, every application status,
each evidence state, and rule precedence. Treat a gold scenario failure as a policy regression.

## Where to look next

| When you are | Read |
| --- | --- |
| Editing YAML under `rules/` | [rules/AGENTS.md](rules/AGENTS.md), then [rules/README.md](rules/README.md) for the DSL |
| Working in `alternate-options/` | [alternate-options/AGENTS.md](alternate-options/AGENTS.md) |
| Asked why the design is this way | [docs/technical-design-document.md](docs/technical-design-document.md) section 4.1, decisions D1 to D8 |
| Touching accuracy or the judges | [evals/README.md](evals/README.md) |
| Touching the test personas | [samples/README.md](samples/README.md) |

## Running things that cost money

`admissions extract` and `admissions screen` call OpenAI. Everything in `alternate-options/` and
`tools/rule-extractor/` spends tokens on every run, and a full alternate-options run is 27 personas
times 3 repeats times 2 arms. Ask before starting one.

`ADMISSIONS_OPENAI_MODEL` sets the model for the service and both alternatives.
`admissions evaluate` needs no key at all, because it replays saved facts through the rules
engine.

`runs/`, `output/`, and `tmp/` are local scratch and are gitignored. The committed evidence lives
in `alternate-options/*/runs/` and `docs/evidence/`, so treat those as results rather than as output
to regenerate casually.
