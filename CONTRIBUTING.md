# Contributing

TurkTokenizer is quality-gated research. Contributions should improve linguistic coverage, reproducibility, or measured generalization without weakening the evaluation protocol.

## Required discipline

1. State the linguistic or architectural hypothesis before training.
2. Change one ablation family at a time and precommit its allowed data, seed, metrics, keep/drop rule, and regression limits.
3. Add deterministic unit or audit cases for Turkish casing, apostrophes, vowel harmony, consonant alternations, derivation, and inflection when relevant.
4. Report per-family precision, recall, F1, macro F1, minimum-family F1, UAS, and LAS; do not report only a favorable aggregate.
5. Preserve the sealed validation and external-holdout policy.
6. Do not inject gold candidates, oracle tags, hidden labels, or post-hoc evaluation thresholds.
7. Do not commit corpora, serialized datasets, checkpoints, or private paths.

An ablation that improves one metric while violating a locked regression bound should be reported honestly and rejected under its precommit.
