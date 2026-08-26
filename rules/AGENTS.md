# Program rule authoring

Use these instructions when you translate policy documents into executable program rules in this directory.

## Required inputs

The task must provide one or more policy sources as PDF or Markdown files and one or more target programs. Use an existing program from `../config/programs.yaml` when it matches the request. A new program needs an ID, display name, study level, program subject, policy ID, and initial policy version.

When both PDF and Markdown copies exist for the same source, treat the PDF as authoritative unless the user names the Markdown file as the source. Use the Markdown copy to find relevant text, then verify headings, tables, exceptions, and footnotes against the PDF.

Read `./README.md` before editing. It is the source of truth for the YAML structure, DSL constructs, evaluation behavior, file hierarchy, and rule scope. Read the existing policy, rule, and common YAML files as working examples.

## Extract the program requirements

Read the relevant source sections and enough surrounding text to understand their scope. For every requirement, identify:

- The source file, PDF pages or Markdown heading, and policy section.
- The programs to which the requirement applies.
- The conditions, thresholds, exceptions, and resulting status.
- The information whose absence or uncertainty prevents a decision.

Separate source requirements from implementation choices. Report unclear, conflicting, or unstated behavior instead of inventing a rule.

## Check current engine support

Map each requirement to existing rule IDs, candidate collections, facts, values, operators, statuses, and conditions. Check the current YAML and the Python definitions under `../app/models/` and `../app/rules_engine/` instead of assuming a value exists.

The rules only workflow does not extend the Python engine. If a requirement needs a new engine value or construct, report the required extension and the affected source section. Do not create YAML that the current compiler cannot activate.

## Design the files

Create one policy entry file for each program that needs different applicability or resolution. Programs with the same rule meaning should import the same rule groups instead of copying them.

Group rules by the policy area they evaluate. Follow the policy, module, import, export, namespace, and rule group patterns in the existing YAML files.

Reuse `common/requirements.yaml` when an existing requirement has exactly the same meaning. Add a new shared requirement only when more than one rule uses that meaning. Apply the same rule to `common/conditions.yaml`.

Use existing rule files as structural examples only. The supplied source documents determine the new policy meaning.

## Write the rules

Follow the DSL and evaluation behavior in `./README.md`.

- Record every policy source in the policy `sources` field with its file, section, and subsections.
- Use `require` and `result` for one three valued requirement. Use ordered `branches` for several distinct outcomes.
- Define false and unknown outcomes explicitly. Every branch group must contain `unknown` and `otherwise` results.
- Preserve candidate precedence and application resolution order unless the source requires different behavior.

Every reason code must have a stable explanation in `../app/rules_engine/reason_catalog.py`. Keep rule IDs, reason codes, module IDs, and policy IDs stable after release.

Increase the last numeric part of every changed YAML module version. Increase a policy patch version when its executable behavior can change, then update every matching program config, fixture, and saved test artifact reference.

## Add reviewed scenarios

Add or update scenarios under `../test/fixtures/rules_engine/` and their assertions under `../test/rules_engine/`. Cover each changed result with facts that produce `TRUE`, `FALSE`, and `UNKNOWN` where applicable.

Unknown coverage must include relevant `MISSING`, `UNREADABLE`, and `CONFLICTING` facts. A numeric threshold must have cases immediately below, at, and immediately above each boundary. Add precedence scenarios when several candidates or rules can match.

Expected results must follow the source mapping and the evaluator behavior in `./README.md`. Tests must not introduce policy meaning that the source does not contain.

## Verify and report

First, run the rule engine tests:

```console
uv run pytest -q test/rules_engine
```

Run the full offline suite when a policy version, program config, or shared definition changes:

```console
uv run pytest -q
```

The work is complete when every program points to an active policy, every rule has a source entry, every reason code has an explanation, policy compilation succeeds, and the required tests pass.

In the final report, list the input programs, changed policies and rules, supporting PDF pages or Markdown headings, unsupported requirements, version changes, and exact test results.
