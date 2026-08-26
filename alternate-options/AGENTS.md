# Working in alternate-options

Three architectures that put the admission decision inside a model, kept because they were
measured and lost. They are evidence, not products. The comparison and its caveats are in
[README.md](README.md), and the reasoning is in [../docs/technical-design-document.md](../docs/technical-design-document.md) under D1.

Read [../AGENTS.md](../AGENTS.md) first for the repository-wide rules.

## Clean room

Neither alternative imports from `app/`. That is what makes the comparison mean anything, because
an alternative that borrowed the rules engine would be measuring the rules engine. Each folder is
its own uv project with its own `pyproject.toml` and lock file, and each is run from inside its
own folder.

Three things are deliberately shared, and only these three. The applicant PDFs in
`../samples/filled-documents/`, the five-value status vocabulary, and the policy handbook in
`../case-study/`. The handbook is the input, not the curated rules in `../rules/`, so no
alternative gets to free-ride on the rule extractor. It is IU's document and is not in the
repository, so both folders fail with a message naming the path when it is absent.

## The two folders

**[option-b-full-policy-workflow/](option-b-full-policy-workflow/)** sends the whole
93,500-token handbook plus the applicant's documents through two model calls per application.
Everything lives in `full-policy-workflow.ipynb`, so a change means editing the notebook.

**[option-cd-agentic-rag/](option-cd-agentic-rag/)** reads the handbook once and caches the
criteria, then evaluates each application with a critic that may force one retry. Options C and D
are two arms of this one codebase, `toc` and `rag`, and they differ only in how the agent finds
policy text. A change that helps one arm and not the other is a change to the experiment, so say
so. `src/config.py` holds every knob, and `uv run pytest` covers the pure-code seams offline.

## Committed evidence

`runs/` in each folder holds results rather than scratch, and the numbers in the design document
come from `runs/eval-summary.json`. What is not committed is what a command regenerates, meaning
`baseline/` from `./baseline.sh`, the Chroma index from `compile_policy`, and the raw model
responses. Regenerating any of them spends tokens.

`runs/ledger.jsonl` is append-only across sessions, so a stray run inflates the cost totals in
`eval-summary.json` even when accuracy is unchanged. Run experiments against a scratch directory,
or restore `runs/` afterwards, so the committed evidence keeps matching the design document.

The key `naive` in the evidence files and in `evaluate.py` is option B under its original name.
It is the schema of committed JSON, so leave it and change only display strings.

## Before running anything

Every command here spends real tokens, and a full run is 27 personas times 3 repeats times 2
arms. Ask first.

`ADMISSIONS_OPENAI_MODEL` sets the model for both folders and for the service, with
`TWO_AGENTS_MODEL`, `AGENTIC_RAG_MODEL`, `CRITIC_MODEL`, and `AGENTIC_RAG_EMBED_MODEL` as
overrides. Keep them equal across the arms. The committed runs did not, and that is the open
caveat on every number in section 4.2.
