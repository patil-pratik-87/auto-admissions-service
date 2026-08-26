# Case study source material

The documents IU supplied for the case study. They are IU's property and are included here so
the alternate options and the rule extractor run from a clean clone.

The handbook is the policy every option works from, in three formats. Only the markdown is read
by code, and the PDF and HTML are the originals it was converted from.

```
IU-FS-LF-Leitfaden-Hochschulzugangsberechtigung-Stand-Januar2025.md    read by code
IU-FS-LF-Leitfaden-Hochschulzugangsberechtigung-Stand-Januar2025.pdf   original
IU-FS-LF-Leitfaden-Hochschulzugangsberechtigung-Stand-Januar2025.html  original
```

Three things read the markdown, and each fails with a message naming the path when it is absent.

| Reader | What it does with the handbook |
| --- | --- |
| [../tools/rule-extractor/](../tools/rule-extractor/) | Drafts YAML rules from it, once per policy release |
| [../alternate-options/option-b-full-policy-workflow/](../alternate-options/option-b-full-policy-workflow/) | Sends the whole thing to a model on every application |
| [../alternate-options/option-cd-agentic-rag/](../alternate-options/option-cd-agentic-rag/) | Reads it once through an agent and caches the criteria |

The shipped service never reads it. `app/` evaluates the approved YAML in [../rules/](../rules/),
which is this project's own encoding of the policy and is the deliverable.

## What is not here

The briefing recording and its transcript are excluded. The recording walks through a live case
in IU's CRM and names a prospective student along with their programme and start date, which is
personal data that does not belong in a public repository. No code reads it.
