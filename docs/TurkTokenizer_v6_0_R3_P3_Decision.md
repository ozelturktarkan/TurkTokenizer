# TurkTokenizer v6.0 R3-P3 decision

R3-P3 asked whether the direct-family ranking signal learned by R3-P2 could be
isolated from its family regressions. The corrected v2 experiment copied exactly
123 direct-family tensors from the closed R3-P2 candidate onto the completed,
frozen R1 checkpoint. All other 216 tensors came from R1. No optimizer step was
taken.

## Protocol correction

The original v1 masked-training design began from the selected R1 Syntax E10
boundary. That boundary preceded the completed R1 relation and hard-negative
state, so its frozen protected branches were not a valid final-R1 comparator.
The run was stopped after Relation E01 and before E02. Those E01 values are
retained as protocol diagnostics only; they are not an R3-P3 result and no
promotion decision was permitted.

R3-P3 v2 corrected the question without introducing a new training variable:
completed R1 supplied the protected state and R3-P2 supplied only the existing
direct-family tensors. The graft smoke proved bit-identical protected state and
outputs before CALIB was opened.

## CALIB result

| Metric | R1 protected base | R3-P2 ranking candidate | R3-P3 v2 graft |
|---|---:|---:|---:|
| Macro relation F1 | 0.8078 | 0.8141 | 0.7795 |
| Minimum-family F1 | 0.7138 | 0.7247 | 0.7139 |
| POSS_HEAD F1 | 0.8123 | 0.8269 | 0.7594 |
| OBJECT F1 | 0.7138 | 0.7247 | 0.7139 |
| PARTICIPLE_HEAD F1 | 0.8232 | 0.8346 | 0.7628 |
| CASE_GOVERNOR F1 | 0.8820 | 0.8704 | 0.8820 |
| UAS | 0.8831 | 0.8868 | 0.8831 |
| LAS | 0.7643 | 0.7678 | 0.7643 |
| Micro direct head top-1 | — | 0.9406 | 0.9307 |

R3-P3 v2 passed 3 of 12 gates: the `CASE_GOVERNOR`, UAS, and LAS
regression limits. Those protected metrics equal R1 exactly. It failed the nine
direct-family, aggregate, factorized OBJECT, and matched-control gates. Relative
to R3-P2, macro F1 fell by `0.0346`, POSS_HEAD by `0.0675`,
PARTICIPLE_HEAD by `0.0718`, OBJECT by `0.0108`, and micro direct head
top-1 by `0.0099`.

The precommitted decision is `DROP_AFTER_SCREEN`. Post-hoc rescue is
prohibited.

## Conclusion

The R3-P2 ranking gain is not localized in the final direct-family scorer
modules. It depends on the shared representation and calibration learned with
those modules. The graft cleanly preserves R1's protected CASE and syntax
behavior, but the donor scorers are incompatible with the R1 representation.

This closes the R3 line. A next mainline must learn ranking-compatible shared
representations while explicitly preventing cross-family and syntax gradient
interference; that work is R4, not another R3 patch.

The final outputs and audit checkpoint were independently retained and
re-materialized in two checksum-verified private closure packages.
`INTERNAL_VAL`, official TEST, and external holdouts remain unopened.
