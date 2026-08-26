# Rule extractor

A prototype answering one question. Can a model pipeline re-derive compilable admission rules
from the IU handbook, so that writing rules for a new program is not the new bottleneck?

Nothing here is imported by the service. No generated rule ships without a person reading and
approving it, and the compiler rejects a broken package before it can screen anyone.

## Run

```console
uv run --with jupyter jupyter lab tools/rule-extractor/rule_extractor_demo.ipynb
```

Run the cells top to bottom. The key comes from the repository root `.env`, and
`ADMISSIONS_OPENAI_MODEL` sets the model. This spends tokens.

## What is here

| Path | What it is |
| --- | --- |
| `rule_extractor_demo.ipynb` | The pipeline, Bachelor rules, three arms |
| `master_run.py` | A one-off run proposing Master rules, arms B and C |
| `generated-rules-master-c/` | The kept example, arm C of the Master run |

The Bachelor arm outputs and the saved intermediates, meaning the navigation trace, the
requirements, and the mapping, are not committed. A run writes them again into
`generated-rules-*/`, `artifacts/`, and `master-artifacts/`.

The Master run is the useful negative result. The engine cannot compile Master rules, because
`study_level` is fixed to `BACHELOR` and the rule IDs are Bachelor IDs, so the model proposed new
vocabulary and the compile step recorded the rejection rather than repairing it. That is the
design working, since an unencodable rule becomes `MANUAL_REVIEW` rather than a guess.

The reasoning is in [../../docs/technical-design-document.md](../../docs/technical-design-document.md) under D5.
