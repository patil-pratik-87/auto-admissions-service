# Sample builder

Twelve standalone scripts that turn a persona YAML file into the PDFs an admissions office would
receive. They overlay synthetic data on the real blank certificates in
[../../samples/blank-documents/](../../samples/blank-documents/), at coordinates measured from each
template.

Each script declares its own dependencies inline, so `uv run` handles them with no project
install.

```console
uv run tools/sample-builder/fill_abitur.py samples/filled-documents/felix-brandt/felix-brandt.yaml
```

The `fill_*` scripts stamp an official blank form. The `make_*` scripts build a document from
nothing, for the certificate types where no usable blank exists. Most also write a second file
ending in `-scan.pdf`, which is a 150 dpi raster of the same page with no text layer, and those
are the unreadable cases in the test set.

Every script names its template and its usage line in its docstring, and writes to
`samples/filled-documents/<slug>/`. No script calls a model or reaches the network.

What the set covers and why is in [../../samples/README.md](../../samples/README.md).
