# S02 source overlay

These modules are the S02 v0.1.0 changes to the private S01-CP1 research package.
Place them in that package's root, alongside its `bootstrap.py`, `r2_analyzer.py`
and `context_proposals.py`. Parent runtime modules, dictionaries and model
weights are required and are not redistributed here.

Run from the authorized package root:

```bash
python -X utf8 runtime_s02.py --file input.txt --output output.json
```

`--context-model s01` is the default. `ensemble` and `residual` require their
corresponding optional research model files. `--no-context` skips contextual
selection. Original character offsets and alternative analyses are preserved.

`segmentation_s02.py` and `numerals_s02.py` use the Python standard library and
can also be used independently. See the aggregate S02 decision note in `docs/`
for validation results and unresolved limitations.
