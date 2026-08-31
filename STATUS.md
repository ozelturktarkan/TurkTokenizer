# Project status — 2026-08-30


## Reliable state


- v3S and the locked v4 baseline are rejected before `INTERNAL_VAL`.
- v4.1 A1 remains the strongest surviving base, but failed the absolute CALIB gates.
- v4.1 A2 and A3 are closed as `DROP_AFTER_SCREEN`.
- v4.2 R1 is precommitted and its architecture smoke gate is `PASS`.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.


## Live v6.0 R2-P9 repair line


R2-P9 restored the selected Syntax E20 boundary and migrated it safely onto the repaired morphology lattice. The public smoke gate passed. The current selected and resume boundaries are recorded below; all figures are preliminary TRAIN/CALIB screening results, not final model claims.


The Syntax ceiling is now E70; Relation and Hard-Negative ceilings remain E50. Patience remains 9 in every stage and resets to `0/9` on a qualifying improvement. A deterministic learning-rate reduction applies at the fourth consecutive non-improving epoch. For Syntax, a three-epoch overfitting guard stops safely when selection score does not improve while training loss falls and CALIB syntax loss rises by at least 0.1% per epoch; on a stop, the highest-scoring checkpoint is frozen and independently archived twice. The explicit Relation overfitting guard is intentionally deferred until after E40; before that boundary, the nine-epoch patience and deterministic plateau-LR policy remain the active safeguards. LAS `0.80` and selection score `0.85` are tracking targets, not claims or reasons to open sealed evaluation. Sealed evaluation remains unopened.


Syntax training closed safely at E42 after the overfitting guard fired at `3/3`. Syntax E38 remains frozen as the selected parent checkpoint: `loss=0.1365`, `UAS=0.8867`, `LAS=0.7670`, `UPOS=0.9252`, selection score `0.81872136`. Relation training closed at E37 after patience reached `9/9`; E28 is frozen as the Relation checkpoint with selection score `0.78178072`. Hard-Negative H11 produced a new selected stage best with `loss=0.0669`, macro F1 `0.8014`, minimum-family F1 `0.7122`, `POSS_HEAD=0.795`, `OBJECT=0.712`, `PARTICIPLE_HEAD=0.825`, `CASE_GOVERNOR=0.873`, `UAS=0.8838`, `LAS=0.7642`, and selection score `0.78127320`. H11 exceeded the previous H06 best score `0.77920893`; H11 is now selected. Patience reset `4/9 → 0/9`, LR remains `0.00006` after the H10 plateau reduction, and the full source hard-negative penalty remains `0.250000`. The H11 rolling state, unchanged cache, and new H11 stage-best checkpoint are stored independently in two private durable packages; H12 is the next boundary. INTERNAL_VAL, external holdouts, and official TEST remain unopened. These are TRAIN/CALIB screening results, not sealed-test claims.


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
