# Working in evals

Two checks, on two different halves of the system. Read [README.md](README.md) for what they are
and [../AGENTS.md](../AGENTS.md) for the repository-wide rules.

Nothing here can change an applicant result. `app/` never imports from `evals/`, and it must stay
that way.

## The split that decides where a check belongs

Gold scenarios take facts in and check the status out, so they pin the evaluator and are silent
on extraction. Judges look at the PDFs and ask whether the facts were read correctly. When you
add a check, decide which half it belongs to first, because putting an extraction check in the
gold scenarios makes it untestable and putting an evaluator check in a judge makes it unreliable.

## Reach for code before reaching for a judge

Every synthetic PDF was generated from a persona YAML in `../samples/filled-documents/`, so the intended
facts are known by construction. A deterministic comparison against those is exact, free, and
instant, and a judge is none of those. Add a judge only where the answer needs reading rather
than comparing, and say in the criterion why code cannot do it.

`OMITTED_EVIDENCE` shows the trap. It first asked whether anything legible and relevant was left
out, and it failed every persona by flagging foreign-language grades and Latinum, which the
closed facts schema has no field for. It was measuring the schema, not the extractor. The
criterion now scopes itself to fields the facts already define.

## Rules for a judge criterion

One failure mode per judge, binary PASS or FAIL, and no scores or partial credit. Say what the
judge must not do as well as what it must; each criterion already excludes recalculating policy
thresholds, interpreting the DSL, and validating identifiers, because those are deterministic
elsewhere. Do not ask a judge to predict what the rules engine will do, since you can run it.

`build_judge_instructions` enforces the rest. Two to four examples, TRAIN split only, both labels
present, and at least one borderline case. Those checks exist so measurement can never be taken
against an example the prompt already saw.

## Running the live eval

```console
uv run pytest -m live_openai -q
```

Fifteen cases, five personas by three judges, about 70 seconds and a few cents on
`gpt-5.4-mini`. `JUDGE_EVAL_MODEL` overrides the model. It spends tokens, so ask before running
it, and it is deselected from `uv run pytest` for that reason.

Failures are the point. The eval reports what the extractor and the judges actually did, so
never adjust a persona, a threshold, or an expected status to turn it green. Read the critique
and decide whether extraction regressed or the judge is wrong.

Judge calls trace to the `auto-admissions-judges` LangSmith project, kept separate from screening
so a judge call is never read as a decision an applicant received. Each verdict is saved beside
the artifacts it judged, as `runs/judges-live/<persona>/judge-<name>.json`, and the run writes
`runs/judges-live/report.md` on teardown with the screening table, the verdict matrix, every
critique behind a FAIL, and the token cost. Rebuild it from what is already on disk with:

```console
uv run python -m evals.judges.report
```

## What is not true yet

No judge is calibrated. No domain-expert labels exist, so `measure_judge` has never run on real
data and the few-shot examples in `run_judge.py` stand in for labels. Any statement that a judge
is accurate is unsupported until that changes. Say so rather than implying otherwise.
