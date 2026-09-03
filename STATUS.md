# Project status — 2026-09-03


## Reliable state


- v3S and the locked v4 baseline are rejected before `INTERNAL_VAL`.
- v4.1 A1 remains the strongest surviving base, but failed the absolute CALIB gates.
- v4.1 A2 and A3 are closed as `DROP_AFTER_SCREEN`.
- v4.2 R1 is precommitted and its architecture smoke gate is `PASS`.
- v6.0 R3-P2 control is complete; candidate Relation completed at E50 and
  candidate Hard-Negative E15 is persisted and verified.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.


## Live v6.0 R3-P2 paired line


The matched control arm is complete. Candidate Relation advanced through E50,
its precommitted ceiling. The final Relation state, selected checkpoint,
completion marker, local mirror, and two independent persistent closure
packages were verified. Candidate Hard-Negative E15 then completed; its active
and durable state, fixed cache, selected checkpoint, and two independent
persistent packages were verified. E16 is the next authorized invocation.


Control and candidate CALIB metrics remain blinded until the candidate arm
also closes. No checkpoint, private hash, serialized state, corpus-derived
artifact, split inventory, or sealed-resource metadata is published here.
`INTERNAL_VAL`, official TEST, and external holdouts remain unopened.


## Live v6.0 R2-P9 repair line


R2-P9 restored the selected Syntax E20 boundary and migrated it safely onto the repaired morphology lattice. The public smoke gate passed. The current selected and resume boundaries are recorded below; all figures are preliminary TRAIN/CALIB screening results, not final model claims.


The Syntax ceiling is now E70; Relation and Hard-Negative ceilings remain E50. Patience remains 9 in every stage and resets to `0/9` on a qualifying improvement. A deterministic learning-rate reduction applies at the fourth consecutive non-improving epoch. For Syntax, a three-epoch overfitting guard stops safely when selection score does not improve while training loss falls and CALIB syntax loss rises by at least 0.1% per epoch; on a stop, the highest-scoring checkpoint is frozen and independently archived twice. The explicit Relation overfitting guard is intentionally deferred until after E40; before that boundary, the nine-epoch patience and deterministic plateau-LR policy remain the active safeguards. LAS `0.80` and selection score `0.85` are tracking targets, not claims or reasons to open sealed evaluation. Sealed evaluation remains unopened.


Syntax training closed safely at E42 after the overfitting guard fired at `3/3`. Syntax E38 remains frozen as the selected parent checkpoint: `loss=0.1365`, `UAS=0.8867`, `LAS=0.7670`, `UPOS=0.9252`, selection score `0.81872136`. Relation training closed at E37 after patience reached `9/9`; E28 is frozen as the Relation checkpoint with selection score `0.78178072`. Hard-Negative training closed safely at H21 after patience reached `9/9`. H21 finished with `loss=0.0509`, macro F1 `0.8013`, minimum-family F1 `0.7100`, `POSS_HEAD=0.801`, `OBJECT=0.710`, `PARTICIPLE_HEAD=0.824`, `CASE_GOVERNOR=0.870`, `UAS=0.8847`, `LAS=0.7651`, and selection score `0.78079397`. H21 did not exceed the selected H12 best score `0.78176522`; H12 remains the selected hard-negative checkpoint. LR remained `0.00003` and the full source hard-negative penalty remained `0.250000`. The final CALIB screen reported macro F1 `0.80204292`, minimum-family F1 `0.71206775`, `UAS=0.88431126`, and `LAS=0.76538773`, yielding `DROP_AFTER_SCREEN`. The H21 final state, unchanged cache, preserved H12 stage-best checkpoint, and hard-negative completion marker are stored independently in two private durable packages. INTERNAL_VAL, external holdouts, and official TEST remain unopened. These are TRAIN/CALIB screening results, not sealed-test claims.


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
