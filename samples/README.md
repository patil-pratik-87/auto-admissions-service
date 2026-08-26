# Synthetic applicants

No real applications were available, and real applicant documents are personal data, so the test
set was built rather than collected. It is the input for the rules engine, for the three
alternatives, and for the accuracy numbers in the design document.

The set was written from failures backwards. Four ways the pipeline can break were written down
first, then one case was written for each, then the documents were made to fit. Every case exists
because a specific failure was predicted for it.

| Step | What was done |
| --- | --- |
| 1. Name the error modes | Extractor misses or cannot read a field, fact builder merges two documents wrongly, evaluator treats unknown as false, resolution rejects although another rule passed |
| 2. Write the tuples | 31 triples of rule, decision case, and input condition, with the expected result recorded before any document existed. See [blank-documents/eval-tuples.md](blank-documents/eval-tuples.md) |
| 3. Get real blank forms | 18 official blank certificates, such as the KMK Abitur Musterentwurf, so the layout matches what an admissions office receives |
| 4. Write fill scripts | 12 scripts in [../tools/sample-builder/](../tools/sample-builder/) overlay synthetic data at coordinates measured from each template |
| 5. Generate the bundles | 27 folders in `filled/`, each with a YAML of the intended facts and the PDFs a rule has to read |

## What is here

`blank-documents/` holds the 18 official templates and the tuple table. `filled/` holds the 27
applicant bundles, one folder per persona. Each folder carries a YAML file of the facts the
documents were built to state, which is the ground truth for that persona.

Most fill scripts also emit a 150 dpi raster of the same certificate, named `-scan.pdf`. Those
are how the unreadable cases are made, because a scan removes the text layer.

## Rebuild one

```console
uv run tools/sample-builder/fill_abitur.py samples/filled-documents/felix-brandt/felix-brandt.yaml
```

Each script names its own template and its usage line in its docstring.

## Two things to know

The set is deliberately hard. Each persona carries several ways to fail at once, for example a
missing transcript together with an expired language certificate, so absolute accuracy on it is
lower than a real intake would give. Only the comparison between systems carries over.

The tuples are mirrored as 31 scenarios in `test/fixtures/rules_engine/scenarios.yaml`, and 15 of
them run as gold scenarios on every change to the rules. See [../evals/README.md](../evals/README.md).
