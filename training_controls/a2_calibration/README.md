# A2: frozen A1 E05 / A3 E00 calibration

This isolated stage completes the A1 → A3 → A2 experiment. It performs one full CALIB evaluation, then chooses from the previously declared 121 margin pairs. It does not train epochs or open TEST. Historical experiments and the default model remain unchanged.

The objective is maximum accepted coverage subject to empirical CALIB precision ≥92% for both lemma+POS and the fixed declared-feature schema. The selected subset's precision is not all-word accuracy or coverage. Confidence intervals are nominal descriptive Wilson intervals; selection on the same CALIB data and document dependence preclude interpreting them as a held-out guarantee. Full morpheme paths and actual BPE routing are not evaluated.

Run from the project root with Python 3.11 and `PYTHONDONTWRITEBYTECODE=1`:

```text
python -X utf8 -m unittest training_controls.a2_calibration.test_calibration
python -X utf8 -m training_controls.a2_calibration.calibrate
```

The runner refuses to overwrite its A2 directory. Inputs, source, parent checkpoint hashes and runtime model files are verified before and after evaluation. It checks candidate inventory, complete search, reconstruction, graph consistency and full objective scores. Selected and zero-threshold gates are compared against actual online decisions for every CALIB sentence, with preferred analyses preserved.

All corpus rows, replay outputs, weights and two verified snapshots stay in `V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs\a1-large-20260908-v1\A2`. Two copies on one drive do not protect against physical drive failure. Only source, aggregate results, logs and hash receipts are published to the separate GitHub A2 branch. No default promotion occurs.
