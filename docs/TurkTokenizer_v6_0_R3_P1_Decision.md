# TurkTokenizer v6.0 R3-P1 decision

R3-P1 tested one frozen-checkpoint change on CALIB: the R1 null-arc model activated direct relations from source probability alone instead of source probability multiplied by maximum head probability. Head choice, model parameters, CASE_GOVERNOR policy, and syntax outputs were unchanged.

## Result

| Variant | Macro F1 | Minimum-family F1 | OBJECT F1 | UAS | LAS |
|---|---:|---:|---:|---:|---:|
| A1 reference | 0.810756 | 0.717407 | 0.717407 | 0.878516 | 0.759907 |
| R1 parent | 0.807827 | 0.713783 | 0.713783 | 0.883053 | 0.764309 |
| R3-P1 | 0.805125 | 0.711779 | 0.711779 | 0.883053 | 0.764309 |

R3-P1 reduced OBJECT by `-0.002004` and macro F1 by `-0.002702` versus R1. It remained `-0.005627` below A1 on OBJECT and failed every promotion gate except the unchanged CASE_GOVERNOR policy.

The precommitted decision is `DROP_AFTER_SCREEN`. Although R1’s source classifier has competitive aggregate discrimination, source-only activation loses exact true-positive source–head edges. Further post-hoc decision rescue is not justified; any next line must improve source–head ranking during training.

Two independent executions produced byte-identical aggregate results. INTERNAL_VAL, TEST, and external holdouts remain unopened; no model parameters were trained or updated.
