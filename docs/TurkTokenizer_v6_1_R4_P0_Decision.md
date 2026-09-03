# TurkTokenizer v6.1 R4-P0 decision

Decision: `PASS_R4_P0`

R4-P0 completed its precommitted zero-update, TRAIN-only gradient-conflict audit. All 12 balanced batches completed at seed `51104`; all six primitive losses and gradients were finite; the model-state digest was identical before and after; no optimizer was instantiated; and CALIB, `INTERNAL_VAL`, external holdouts, and official TEST were not consumed.

## Routing map

The fixed P2 routing map uses deterministic PCGrad, projecting only negative pairwise dot products, on:

| Eligible shared group | Conflicted task pairs |
|---|---:|
| shared Transformer | 7 |
| relation bridge | 3 |
| syntax bridge | 5 |

The strongest routed mean conflict was `POSS_HEAD ↔ OBJECT` in the syntax bridge (mean cosine `-0.0230`, minimum `-0.1487`, negative in 7/12 batches). The shared Transformer’s strongest mean conflict was `POSS_HEAD ↔ CASE_GOVERNOR` (mean `-0.0134`), while the relation bridge’s was `POSS_HEAD ↔ PARTICIPLE_HEAD` (mean `-0.0061`, negative in 9/12 batches).

The audit also recorded lexical/morphological conflicts. That block was not PCGrad-eligible in the precommitted executable and is not added post hoc.

## Next phase

R4-P1 is authorized to enter precommit. It must be a fresh repaired-lattice reconstruction with the existing focal objective, no adapter, no PCGrad, and no migrated R2/R1/R3 checkpoint. R4-P2 remains conditional on a completed reproducible P1 parent.

Both final private P0 packages were independently re-materialized and checksum-verified. No sealed evaluation was opened.
