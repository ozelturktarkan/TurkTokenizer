# Project status — 2026-08-21

## v6.0 R2 E50 restart amendment

The first resumable R2 screen was interrupted while relation epoch 5 was
computing. Its last complete relation checkpoint was epoch 4; the corresponding
model/optimizer/RNG state did not survive outside the interrupted workspace, so
it is not reused or reconstructed from metrics.

A fresh fixed-seed R2 screen is therefore precommitted with a common maximum of
50 epochs for syntax, relation, and hard-negative training. Early stopping is
unchanged: an improvement greater than `1e-4` resets patience to `0/5`; every
other completed epoch increments it once; the stage stops after writing state
at `5/5`. The larger ceiling does not change data, architecture, optimizer,
selection scores, gates, or the sealed-evaluation policy.

The amendment is recorded in
`contracts/TurkTokenizer_v6_0_R2_E50_Amendment_v1.json`. `INTERNAL_VAL`,
external BOUN/IMST/Penn holdouts, and official TEST splits remain unopened.

## Reliable state

- v3S and the locked v4 baseline are rejected before `INTERNAL_VAL`.
- v4.1 A1 remains the strongest surviving base, but failed the absolute CALIB gates.
- v4.1 A2 and A3 are closed as `DROP_AFTER_SCREEN`.
- v4.2 R1 passed smoke but is closed as `DROP_AFTER_SCREEN`.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.

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

## Final R1 closure

The fixed-seed resumable TRAIN/CALIB screen completed cleanly. The selected checkpoint was hard-negative epoch 2:

- macro relation F1: `0.8078`
- minimum-family F1: `0.7138` (`OBJECT`)
- `UAS=0.8831`, `LAS=0.7643`, `UPOS=0.9205`
- family F1: `POSS_HEAD=0.8123`, `OBJECT=0.7138`, `PARTICIPLE_HEAD=0.8232`, `CASE_GOVERNOR=0.8820`

Against A1, R1 changed macro by `-0.0029` and minimum-family F1 by `-0.0036`. Family changes were `POSS_HEAD=-0.0067`, `OBJECT=-0.0036`, `PARTICIPLE_HEAD=-0.0143`, and `CASE_GOVERNOR=+0.0128`. R1 therefore failed both the required gain and the no-family-regression condition. The absolute CALIB gate also failed on macro, minimum-family F1, and LAS; only UAS passed.

The factorized audit found `OBJECT` source-token F1 `0.7259` and head top-1 accuracy `0.9327` given the gold source. A1 source-token F1 was `0.7288`, so NULL-plus-head normalization did not solve the targeted source-identification bottleneck.

All final states, selected/frozen checkpoints, calibration, audits, gates, logs, and transfer-safe shards are mirrored outside the scratch worktree and in ChatGPT Library. `INTERNAL_VAL` and all external holdouts remain unopened.

Next: freeze R1 as a negative result, retain A1 as the strongest surviving base, and precommit the next error-led ablation before training.
