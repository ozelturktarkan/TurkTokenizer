# Project status — 2026-08-29

## Reliable state

- v3S and the locked v4 baseline are rejected before `INTERNAL_VAL`.
- v4.1 A1 remains the strongest surviving base, but failed the absolute CALIB gates.
- v4.1 A2 and A3 are closed as `DROP_AFTER_SCREEN`.
- v4.2 R1 is precommitted and its architecture smoke gate is `PASS`.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.

## Live v6.0 R2-P9 repair line\n\nR2-P9 restored the selected Syntax E20 boundary and migrated it safely onto the repaired morphology lattice. The public smoke gate passed. The latest independently archived resume boundary is Syntax E21 with `next_epoch=22` and patience `1/9`; this is a preliminary TRAIN/CALIB state, not a final model claim.\n\nSyntax, relation, and hard-negative ceilings are E50. Patience is 9 in every stage and resets to `0/9` on a qualifying improvement. A deterministic learning-rate reduction applies at the fourth consecutive non-improving epoch. Sealed evaluation remains unopened.\n\n## Final A3 closure

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
