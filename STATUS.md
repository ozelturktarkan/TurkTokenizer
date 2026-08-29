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

Syntax E38 remains the selected checkpoint: `loss=0.1365`, `UAS=0.8867`, `LAS=0.7670`, `UPOS=0.9252`, selection score `0.81872136`. The operator-requested E38→E39 patience reset preserved model, optimizer/RNG/sampler state, LR, and the E38 best. E41 completed with `loss=0.1237`, CALIB syntax loss `2.2218`, `UAS=0.8857`, `LAS=0.7641`, `UPOS=0.9252`, and selection score `0.81670860`. It did not improve the selected score; patience is `3/9`. Training loss fell while CALIB loss rose and selection did not improve for the second consecutive epoch, so the overfitting streak is `2/3`. The independently archived resume boundary is `completed_epoch=41`, `next_epoch=42`, LR `0.0000625`. If E42 confirms the same signal, Syntax training will stop and the E38 best will be frozen and independently archived twice; Relation will not start automatically. This remains a TRAIN/CALIB screening result, not a sealed-test claim.

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
