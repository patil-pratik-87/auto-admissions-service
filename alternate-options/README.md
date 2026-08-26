# The architectures that were compared

Four ways to turn a 93,500-token policy handbook and a bundle of applicant PDFs into an
admission status. Option A is the one that shipped and lives in [../app/](../app/). The other
three were built here and measured on the same synthetic applicants.

| | Where the policy is read | Where the decision is made |
| --- | --- | --- |
| **A. Rules engine** | Once per release, into YAML | Code, [../app/](../app/) |
| **B. Full policy workflow** | Every application, in full | A model call, [option-b-full-policy-workflow/](option-b-full-policy-workflow/) |
| **C. Agentic RAG, headings** | Once, by opening sections | A model call, [option-cd-agentic-rag/](option-cd-agentic-rag/) |
| **D. Agentic RAG, vectors** | Once, by vector search | A model call, [option-cd-agentic-rag/](option-cd-agentic-rag/) |

Options C and D share one codebase and differ only in how the agent finds policy text, so they
run as two arms of the same experiment rather than as two folders.

## What was measured

| Measure | A | B | C | D |
| --- | --- | --- | --- | --- |
| Accuracy, 14 labeled personas | **13 of 14** | 8 of 14 | 7 of 14 | 9 of 14 |
| Status changed across identical repeats | **0 of 15** | 7 of 15 | 7 of 15 | 9 of 15 |
| Applicants wrongly called ELIGIBLE | **0%** | 3.7% | 22.2% | 14.8% |
| Policy tokens per application | **0** | 93.5k | 3.1k | 2.8k |
| Cost per decision | $0.033 | $0.212 | $0.026 | **$0.025** |

The rules engine is the only option that returns the same status on a repeat run, because code
makes the decision rather than a model. It is also the only one that never admitted an applicant
who does not qualify, which is the failure the design is built to prevent. Sending the whole
handbook on every application costs the most and buys the least accuracy. Retrieval cuts the
policy cost to about 3,000 tokens and does not recover the accuracy.

The full table, the charts, and the reasoning are in [../docs/technical-design-document.md](../docs/technical-design-document.md),
sections 4.1 and 4.2.

## Two things to know before reading the numbers

**The arms were not run on one model.** Option B ran on `gpt-5.6-terra` over 16 personas. Options
C and D ran on `gpt-5.4-mini` over 27 personas, and the three-way evaluation reads option B's
result from its earlier file. Every model is now set by `ADMISSIONS_OPENAI_MODEL`, so a rerun on
one model is a rerun of the same commands. Until then the comparison carries a second variable.

**The personas are deliberately hard.** Each one carries several ways to fail at once, so
absolute accuracy is lower than a real intake would give. Only the comparison between the options
carries over.

## Ground rules

Same applicants, same five-value status vocabulary, and no imports from `app/` in either
alternative. The policy input is the official handbook rather than the curated rules, so no
alternative gets to free-ride on the rule extractor. Each alternative has its own README with
setup and run commands, and both spend tokens when run.
