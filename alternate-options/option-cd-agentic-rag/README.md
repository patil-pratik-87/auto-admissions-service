# Options C and D: agentic RAG

The handbook is read once by an agent and the criteria are cached. Per application a model
decides, and a second model reviews that decision and may force one retry. The two options are
two arms of this codebase, and they differ only in how the agent finds policy text.

| | C, `toc` | D, `rag` |
| --- | --- | --- |
| The agent sees | the table of contents | nothing, it can only search |
| The agent asks for | section headings | up to 3 queries per turn |
| Selection | whole sections, no chunking | Chroma and `text-embedding-3-large`, top 6 |

**The question it answers.** Retrieval cuts the policy cost. Does a retrieval-grounded critic
loop also close the accuracy gap to the rules engine, without anyone writing a DSL?

**The answer.** No. Policy tokens per application fall from 93,500 to about 3,000, and accuracy
does not recover. Option C matched 7 of 14 labeled personas and option D matched 9, against the
rules engine's 13. Both changed their answer across identical repeats, and both wrongly admitted
applicants the rules engine never admitted.

## Run it

```console
uv sync
uv run pytest                          # offline, no API key

uv run python -m src.compile_policy    # once per arm, cached on policy and prompt hash
uv run python -m src.run               # personas x 3 repeats x 2 arms   SPENDS TOKENS
./baseline.sh                          # fresh rule-based runs           SPENDS TOKENS
uv run python -m src.evaluate          # three-way comparison, writes runs/
```

Secrets come from the repository root `.env`. `ADMISSIONS_OPENAI_MODEL` sets the model, and
`AGENTIC_RAG_MODEL`, `CRITIC_MODEL`, and `AGENTIC_RAG_EMBED_MODEL` override it here. The
committed run used `gpt-5.4-mini`. Other knobs live in [src/config.py](src/config.py).

## What is here

- `src/` is the pipeline, meaning the policy index, the compile step, the LangGraph graph, and
  the evaluation.
- `baseline/` holds fresh rule-based runs of the same applicants, so the arms are compared on
  identical input. Not committed, because `./baseline.sh` regenerates it.
- `runs/` holds the evidence, which is `eval-summary.json`, `comparison.csv`,
  `cost-summary.json`, `disagreements.md`, `retrieval-quality.md`, `walkthrough.md`,
  `results.jsonl`, and `ledger.jsonl`. Raw responses and the Chroma index were removed to keep
  the repository small, and `compile_policy` rebuilds the index.
- `SPEC.md` is the full decision record for this experiment.

## Stated limits

The `rag` arm retrieves whole sections rather than smaller chunks, which keeps it to one variable
against the `toc` arm and gives it an easier job than production RAG usually has. The critic
reads the evaluator's evidence quotes rather than the applicant PDFs, because re-reading them
would make it a second evaluator at double the cost.
