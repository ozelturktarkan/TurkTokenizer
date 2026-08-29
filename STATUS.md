# Project status — 2026-08-29

## Reliable state

- v3S and the locked v4 baseline are rejected before `INTERNAL_VAL`.
- v4.1 A1 remains the strongest surviving base, but failed the absolute CALIB gates.
- v4.1 A2 and A3 are closed as `DROP_AFTER_SCREEN`.
- v4.2 R1 is precommitted and its architecture smoke gate is `PASS`.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.

## Live v6.0 R2-P9 repair line

R2-P9 restored the selected Syntax E20 boundary and migrated it safely onto the repaired morphology lattice. The public smoke gate passed. The current selected and resume boundaries are recorded below; all figures are preliminary TRAIN/CALIB screening results, not final model claims.

The Syntax ceiling is now E70; Relation and Hard-Negative ceilings remain E50. Patience remains 9 in every stage and resets to `0/9` on a qualifying improvement. A deterministic learning-rate reduction applies at the fourth consecutive non-improving epoch. For Syntax, a three-epoch overfitting guard now stops safely when selection score does not improve while training loss falls and CALIB syntax loss rises by at least 0.1% per epoch; on a stop, the highest-scoring checkpoint is frozen and independently archived twice. LAS `0.80` and selection score `0.85` are tracking targets, not claims or reasons to open sealed evaluation. Sealed evaluation remains unopened.

Syntax training closed safely at E42 after the overfitting guard fired at `3/3`. Syntax E38 remains frozen as the selected parent checkpoint: `loss=0.1365`, `UAS=0.8867`, `LAS=0.7670`, `UPOS=0.9252`, selection score `0.81872136`. Relation E2 is now the selected Relation checkpoint: `loss=0.3652`, macro F1 `0.7892`, minimum-family F1 `0.6926`, `POSS_HEAD=0.779`, `OBJECT=0.693`, `PARTICIPLE_HEAD=0.821`, `CASE_GOVERNOR=0.864`, `UAS=0.8815`, `LAS=0.7577`, and selection score `0.76828890`. It qualified as an improvement, so patience remains `0/9` and LR remains `0.00025`. The independently archived Relation resume boundary is `completed_epoch=2`, `next_epoch=3`, with state and best stored in two private durable packages. INTERNAL_VAL, external holdouts, and official TEST remain unopened. These are TRAIN/CALIB screening results, not sealed-test claims.

## Final A3 closure

The clean resumable A3 run completed all syntax, relation, hard-negative, calibration, audit, and screen stages. Its final CALIB result was:

- macro relation F1: `0.8041`
- minimum-family F1: `0.7053` (`OBJECT`)
- `UAS=0.8778`, `LAS=0.7569`, `UPOS=0.9176`
- family F1: `POSS_HEAD=0.8178`, `OBJECT=0.7053`, `PARTICIPLE_HEAD=0.8325`, `CASE_GOVERNOR=0.8606`

Relative to the locked v4 screen baseline, A3 gained only `+0.0068` macro and `+0.0029` minimum-family F1, while `CASE_GOVERNOR` regressed by `-0.0078`. It therefore failed the precommitted improvement and no-family-regression conditions and was dropped without opening `INTERNAL_VAL`.

The factorized audit found `OBJECT` source-token F1 of `0.6748`, but head top-1 accuracy of `0.9334` when the source token was supplied. Candidate coverage was therefore not the main remaining bottleneck; source-presence calibration was.

## v4.2 R1

R1 starts from A1 and changes only the direct-relation decision for `POSS_HEAD`, `OBJECT`, and `PARTICIPLE_HEAD`: independent source/head probabilities are replaced by a length-normalized categorical distribution over `NULL` plus valid heads. `CASE_GOVERNOR`, A1 morphology, syntax, data, seed, optimizer, schedules, and quality gates remain unchanged.

The R1 smoke test passed on seed `51104`:

- 29,306,087 parameters; finite losses and gradients
- joint-probability sum maximum error: `2.38e-7`
- source-probability identity maximum error: `2.46e-7`
- invalid-head probability: `0`
- `CASE_GOVERNOR` numerical change: `0`
- internal validation and external holdouts loaded: `false`

## Live R1 screen

The single fixed-seed resumable TRAIN/CALIB screen started at `2026-08-21 10:42:12 +03:00` on CPU. The first durable syntax state completed at `10:48:52`:

- syntax epoch 1 loss: `2.5271`
- `UAS=0.7572`, `LAS=0.6216`, `UPOS=0.8627`
- next recoverable boundary: syntax epoch 2

The raw epoch state is mirrored outside the scratch worktree and as hash-verified transfer shards in ChatGPT Library. These are preliminary training metrics, not a CALIB screen decision.

Next: finish the R1 screen and apply the unchanged survival and absolute quality gates.
