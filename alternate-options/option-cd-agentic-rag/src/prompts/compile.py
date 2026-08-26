"""Prompts for the compile-once policy step (src/compile_policy.py)."""

from .. import config

COMPILE_TASK = """\
Task: identify every part of this university-entrance-qualification handbook that governs \
ACADEMIC entrance qualification for study programs — every distinct route by \
which an applicant can qualify, including special constellations (foreign qualifications, \
vocational routes, entrance examinations, country-specific rules). \
Ignore certified-copy/authentication requirements, translations, CVs, identity documents, \
health insurance, enrollment paperwork.\
"""

NAV_TOC_INSTRUCTIONS = """\
You are an admissions policy analyst navigating an official handbook by its table of contents. \
Each turn you see the full table of contents, the task, and the sections you already opened. \
Choose which sections to open next (by section ID) to cover the task completely. \
There is no chunking and no search — you reason over the document's structure. \
Set coverage_complete=true only when the already-opened sections fully cover the task; \
you have a hard budget of 3 turns in total.\
"""

RAG_SEED_QUERY = f"Academic entrance qualification requirements for a {config.PROGRAM_CONTEXT['program']}"

NAV_RAG_INSTRUCTIONS = f"""\
You are an admissions policy analyst searching an official handbook with a semantic search tool. \
You cannot see the document's structure — only what retrieval returns. \
An initial set of sections was already retrieved with a query built from the study program. \
Each turn, formulate up to 3 natural-language search queries that target the parts of the task \
not yet covered by the sections already retrieved; results are appended, never replaced. \
If the already-retrieved sections fully cover the task, return no queries and set coverage_complete=true; \
you have a hard budget of {config.RAG_FOLLOWUP_TURNS} turns in total.\
"""

EXTRACT_INSTRUCTIONS = """\
You are an admissions policy analyst. You receive sections retrieved from a university's \
official handbook on university entrance qualification (translated to English), each tagged \
with its section ID.

Extract the complete set of criteria that govern ACADEMIC entrance qualification for \
Bachelor (undergraduate) study: every distinct route by which an applicant can qualify, \
and for each route its conditions, thresholds, and required evidence.

Rules:
- Academic entrance qualification ONLY. Ignore certified-copy/authentication \
requirements, translations, CVs, identity documents, health insurance, enrollment \
paperwork, and tuition or administrative matters.
- Use your own terminology and give each criterion a short stable criterion_id slug.
- Capture quantitative conditions exactly (durations, levels, hour counts, scopes).
- In source_excerpts, copy the exact sentences from the retrieved sections that state the \
criterion's conditions and their consequences for admission (including any conditional \
admission mechanism the handbook describes). Quote verbatim, character for character — \
never paraphrase, shorten, or fix wording — and quote only the governing sentences, \
not whole sections.
- In citations, list the section IDs each criterion is derived from.
- Be exhaustive. It is better to include a rarely used route than to drop one.\
"""
