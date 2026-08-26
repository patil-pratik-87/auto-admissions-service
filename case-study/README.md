# Case study source material

This folder holds the documents IU supplied for the case study. They are IU's property and are
not redistributed here, so the folder is empty in a fresh clone apart from this file.

To run anything that reads the policy, put the English markdown conversion of the handbook here
under its original name.

```
case-study/IU-FS-LF-Leitfaden-Hochschulzugangsberechtigung-Stand-Januar2025.md
```

Three things read it, and each fails with a clear message when it is absent.

| Reader | What it does with the handbook |
| --- | --- |
| [../tools/rule-extractor/](../tools/rule-extractor/) | Drafts YAML rules from it, once per policy release |
| [../alternate-options/option-b-full-policy-workflow/](../alternate-options/option-b-full-policy-workflow/) | Sends the whole thing to a model on every application |
| [../alternate-options/option-cd-agentic-rag/](../alternate-options/option-cd-agentic-rag/) | Reads it once through an agent and caches the criteria |

The shipped service never reads it. `app/` evaluates the approved YAML in [../rules/](../rules/),
which is this project's own encoding of the policy and is the deliverable.
