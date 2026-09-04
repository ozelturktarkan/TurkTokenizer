# Project status — 2026-09-04


## Reliable state


- v3S and the locked v4 baseline are rejected before `INTERNAL_VAL`.
- v4.1 A1 remains the strongest surviving base, but failed the absolute CALIB gates.
- v4.1 A2 and A3 are closed as `DROP_AFTER_SCREEN`.
- v4.2 R1 is precommitted and its architecture smoke gate is `PASS`.
- v6.0 R3-P2 is closed as `DROP_AFTER_SCREEN`; 10/12 paired CALIB gates
  passed, with two absolute family-regression gates missed.
- v6.0 R3-P3 is closed as `DROP_AFTER_SCREEN`; v2 passed 3/12 gates and the R3 line is closed.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.


## Closed v6.0 R3-P2 paired line


The matched control and candidate arms are complete. Candidate Relation closed
at its precommitted E50 ceiling, Hard-Negative closed at E19, and the selected
checkpoint was screened. The ranking-loss candidate yielded macro F1 `0.8141`,
minimum-family F1 `0.7247`, `UAS=0.8868`, and `LAS=0.7678`. It passed 10 of
12 precommitted gates but missed the absolute `CASE_GOVERNOR` and
`PARTICIPLE_HEAD` regression limits, so the paired decision is
`DROP_AFTER_SCREEN`.

Two independent paired-decision executions and persistent A/B decision packages
were verified. Detailed per-family diagnostics, checkpoints, private hashes,
serialized state, corpus-derived artifacts, split inventories, and
sealed-resource metadata are not published here. `INTERNAL_VAL`, official TEST,
and external holdouts remain unopened. See
[the decision note](docs/TurkTokenizer_v6_0_R3_P2_Decision.md).


## Closed v6.0 R3-P3 family-isolated ranking transfer


R3-P3 v1 was stopped after Relation E01 because the selected Syntax E10 start boundary preceded the completed R1 protected relation state. E02 did not run; v1 is protocol-invalid and its diagnostic values are not an R3-P3 result.


R3-P3 v2 used the completed R1 checkpoint as the protected base and copied exactly 123 direct-family tensors (2,222,643 parameters) from the R3-P2 ranking candidate. All 216 protected tensors (27,083,444 parameters) remained from R1, and no optimizer step was taken. The final CALIB screen yielded macro F1 `0.7795`, minimum-family/OBJECT F1 `0.7139`, `UAS=0.8831`, and `LAS=0.7643`. Family F1 was `POSS_HEAD=0.7594`, `OBJECT=0.7139`, `PARTICIPLE_HEAD=0.7628`, and `CASE_GOVERNOR=0.8820`.


Only 3 of 12 gates passed: the protected CASE_GOVERNOR, UAS, and LAS regression limits, whose metrics equal R1 exactly. All direct-family, aggregate, factorized OBJECT, and matched-control gates failed. The decision is `DROP_AFTER_SCREEN`; post-hoc rescue is closed. The result shows that the R3-P2 ranking gain depends on the jointly learned shared representation and calibration and cannot be transferred as standalone scorer tensors.


Final outputs and the audit checkpoint are retained in two independently re-materialized, checksum-verified private closure packages. The R3 line is closed. `INTERNAL_VAL`, official TEST, and external holdouts remain unopened. See [the R3-P3 decision](docs/TurkTokenizer_v6_0_R3_P3_Decision.md).


## Active v6.1 R4 line


R4 is reserved for a true fresh-syntax mainline, not another checkpoint graft. R4-P0 passed its smoke, start gate, and 12 deterministic TRAIN-only gradient-audit batches with finite losses and gradients, zero optimizer steps, unchanged model state, and no CALIB access; the audit fixed PCGrad routing on the shared Transformer, relation bridge, and syntax bridge. R4-P1 remains the precommitted fresh repaired-lattice reconstruction with no adapter, PCGrad, ranking loss, or checkpoint migration. Syntax E09 through E15 completed without recurrence of the isolated E07 TRAIN-loss anomaly. Fresh Syntax E15 completed from the verified E14 state with TRAIN loss `0.5821`, CALIB syntax loss `1.3974`, `UAS=0.8677`, `LAS=0.7471`, `UPOS=0.9156`, and selection score `0.80011681`. E15 did not improve the locked score, so E13 remains the selected syntax checkpoint and patience advanced to `2/9`. TRAIN loss and CALIB syntax loss both fell from E14, so the precommitted overfit signal remained false; learning rate remains `0.0005` and the syntax overfit streak is `0/3`. Active and durable E15 resume-state mirrors match, and both E15 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. E16 is authorized under the unchanged protocol. Later phases stay conditional on their parents. No R2-P9 E28, R1, or R3 checkpoint is migrated. The suffix/allomorph registry remains outside R4. See [the R4 plan](docs/TurkTokenizer_v6_1_R4_Plan.md), [R4-P0 precommit](docs/TurkTokenizer_v6_1_R4_P0_Precommit.md), [R4-P0 decision](docs/TurkTokenizer_v6_1_R4_P0_Decision.md), and [R4-P1 precommit](docs/TurkTokenizer_v6_1_R4_P1_Precommit.md).


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
