# Option B: full policy workflow

Nothing is prepared in advance. Every application sends the whole 93,500-token handbook and the
applicant's PDFs through two model calls, and the second call decides the status.

**The question it answers.** Can "one agent reads the policy, a second agent reads the documents
and decides" match a facts extractor followed by a deterministic rules engine?

**The answer.** No. It matched the expected status on 8 of 14 labeled personas against the rules
engine's 13, it changed its answer on 7 of 15 personas across three identical repeats, and it
costs about 6 times as much per decision because the handbook is re-sent every time. It was
cheap to build, and it decides cases nobody encoded.

## Run it

```console
uv sync
uv run --with jupyter jupyter lab full-policy-workflow.ipynb
```

Run the cells top to bottom. Secrets come from the repository root `.env`. This spends tokens.

`ADMISSIONS_OPENAI_MODEL` sets the model, and `TWO_AGENTS_MODEL` overrides it for this prototype
alone.`.

## What is here

- `full-policy-workflow.ipynb` is the whole prototype, meaning config, contracts, prompts, the LangGraph
  pipeline, a single-run demo, and the batch collection.
- `runs/` holds the evidence, which is `eval-summary.json`, `comparison.csv`,
  `cost-summary.json`, `disagreements.md`, `prototype-results.jsonl`, and per-call telemetry in
  `ledger.jsonl`. Raw model responses were removed to keep the repository small.
- `baseline/` holds fresh rule-based runs of the same applicants for a like-for-like
  comparison. Not committed, because `./baseline.sh` regenerates it. That spends tokens.

The four-way comparison report this prototype fed into is
[../../docs/measured-comparison.html](../../docs/measured-comparison.html). Its figures for
option C predate the completed run, so read the numbers from
[../../docs/technical-design-document.md](../../docs/technical-design-document.md) section 4.2.

Clean-room rules and the design reasoning are in [../README.md](../README.md) and in
[../../docs/technical-design-document.md](../../docs/technical-design-document.md) under D1.
