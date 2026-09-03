# TurkTokenizer v6.0 R3-P3 precommit

## Question

R3-P2's zero-margin hardest-competitor ranking loss improved the direct-relation screen, but its full-model updates missed the absolute `CASE_GOVERNOR` and `PARTICIPLE_HEAD` regression limits. R3-P3 tests whether the direct-family ranking gain can be retained while isolating updates from shared, syntax, and CASE parameters.

## Sole change from the R3-P2 candidate

Only the trainable-parameter mask changes. The R1 selected Syntax E10 parent, sampler boundary E12, seed 51104, ranking loss, data, features, optimizer, learning rates, weight decay, gradient clipping, CALIB thresholding, selection score, epoch ceilings, patience, and all twelve decision gates remain unchanged.

The existing `POSS_HEAD`, `OBJECT`, and `PARTICIPLE_HEAD` modules under `special_pair`, `morph_pair`, `graph_pair`, `distance_bias`, `fusion_gate`, `source_joint`, `expert_scale`, and `null_arc` are trainable. This is 2,222,643 trainable parameters in 123 tensors out of 29,306,087 total parameters. No parameter or feature is added.

The shared encoder, contextual morphology path, syntax and dependency-relation modules, graph-message layers, and the complete `CASE_GOVERNOR` scoring path are frozen.

## Runtime and smoke gates

The available CPU runtime reproduced the archived R3-P2 candidate Relation E01 checkpoint byte-for-byte: all 339 model tensors and the selection metadata were identical. The parameter-mask smoke then changed 111 allowed tensors, changed no protected tensor, and preserved all ten audited syntax and CASE output groups bit-for-bit.

Both the runtime smoke and the R3-P3 start gate must pass before training.

## Unchanged promotion gates

All twelve gates are required:

| Gate | Requirement |
|---|---:|
| OBJECT F1 | at least 0.719407 |
| Macro relation F1 | at least 0.810756 |
| Minimum-family F1 | at least 0.719407 |
| OBJECT head top-1 given gold source | at least 0.934739 |
| OBJECT source F1 | at least 0.723857 |
| POSS_HEAD regression vs A1 | no more than 0.002 |
| PARTICIPLE_HEAD regression vs A1 | no more than 0.002 |
| CASE_GOVERNOR regression vs R1 | no more than 0.002 |
| UAS regression vs R1 | no more than 0.002 |
| LAS regression vs R1 | no more than 0.002 |
| OBJECT F1 vs closed R3-P2 control | strictly better |
| Micro direct-head top-1 vs closed R3-P2 control | strictly better |

Passing all twelve yields `PROMOTE_TO_FINALIST_PRECOMMIT`; otherwise the decision is `DROP_AFTER_SCREEN`. There is no post-hoc rescue.

## Execution contract

Relation and Hard-Negative stages each have an E50 ceiling and patience 9. A score must exceed the current best by more than (10^{-4}). Learning rate is halved at the fourth consecutive non-improving epoch. Each invocation runs at most one complete epoch, writes atomic primary and mirror state, and is independently archived twice before the next epoch.

Only TRAIN supplies gradients. CALIB is used for checkpoint and threshold selection. `INTERNAL_VAL`, official TEST, and external holdouts remain unopened. R3 closes after this decision; R4 is planned separately.
