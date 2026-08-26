# How accuracy is measured

Two things go wrong independently. The rules can be evaluated incorrectly, and the facts can be
extracted incorrectly from the documents. Only the first is deterministic, so it takes two
different checks.

| Check | Covers | State |
| --- | --- | --- |
| Gold scenarios | The evaluator. Facts in, status out, no model involved | Running on every change |
| LLM judges | The extractor. Whether the facts match the documents | Built, not yet calibrated |

## Gold scenarios

`test/fixtures/rules_engine/scenarios.yaml` holds 31 scenarios written from the evaluation tuples
in [../samples/](../samples/). Fifteen of them run as the policy gate in
`test/rules_engine/test_gold_scenarios.py`, chosen to cover all five rules, every application
status, each evidence state, the professional thresholds, and rule precedence.

They are fast, free, and deterministic. They say nothing about extraction, because the facts are
their input rather than their output.

```console
uv run pytest test/rules_engine -q
```

## LLM judges

The gold scenarios start from facts, so they can prove the evaluator turned facts into the right
status and can never tell you the facts were right. Extraction is where a model reads a PDF, and
that is where the judges look.

Three judges, one per way extraction fails.

| Judge | Question |
| --- | --- |
| `FABRICATED_VALUE` | Does the document actually contain this value? Catches too much |
| `OMITTED_EVIDENCE` | Was something legible and relevant left out? Catches too little |
| `EVIDENCE_STATE` | Is `KNOWN` / `MISSING` / `UNREADABLE` / `CONFLICTING` the right one? Catches wrong uncertainty |

`EVIDENCE_STATE` is the one the design most depends on. D4 rests the whole safety argument on the
four states, and `INELIGIBLE` is reachable only when every rule failed on `KNOWN` facts, so a
model reporting `KNOWN(false)` where the truth is `UNREADABLE` produces a wrongful rejection.

`OMITTED_EVIDENCE` deliberately does not ask whether an omission would change the outcome. That
is computable, by re-running the rules engine with the missing fact supplied, so the judge does
the reading and code does the consequence.

Each judge sees the applicant PDFs, the extracted facts, and the result, and returns a critique
followed by a binary verdict. A judge result never changes an applicant result.

Run all three over five personas from `../samples/filled-documents/`, screening each first. This spends
tokens, so it is deselected from the default suite.

```console
uv run pytest -m live_openai -q
```

It writes `runs/judges-live/report.md` with the screening table, the verdict matrix, and every
critique behind a FAIL, plus one JSON per verdict. Judge calls trace to the
`auto-admissions-judges` LangSmith project. `JUDGE_EVAL_MODEL` sets the model.

For one case on its own:

```console
uv run python -m evals.judges.run_judge runs/judges-live/<persona> --pdf <file.pdf> --judge EVIDENCE_STATE
```

## Calibrating a judge

`measure_judge` scores a judge against domain-expert labels and reports the true positive rate on
human PASS labels and the true negative rate on human FAIL labels. Raw accuracy is not reported,
because a judge that passes everything scores well on it and catches nothing. Few-shot examples
come from a TRAIN split the measurement never touches, which the prompt builder enforces.

A single false PASS on a case flagged `critical_false_automatic_eligibility` rejects the judge
outright, whatever the rates say. Those are the cases where a wrong PASS blesses an applicant
admitted with no caseworker, and a rate is the wrong instrument for them.

**Status.** Built, and not calibrated. No expert labels exist, so no judge has been measured. The
runner uses stand-in few-shots and says so on every run.

## Why judges at all

On the synthetic set, most of what `FABRICATED_VALUE` and `OMITTED_EVIDENCE` check could be a
deterministic comparison instead, because every PDF was generated from a YAML file that records
the intended facts. A gold-facts test would be exact, free, and instant, and it should be written.

The judges are for real applications, where nothing generated the document and ground truth means
a person reading it. You can label a few hundred of those, never fifty thousand, so the judge is
how a labelled sample becomes an estimate over everything else.

The reasoning is in [../docs/technical-design-document.md](../docs/technical-design-document.md) under D2.1 and D2.2.
