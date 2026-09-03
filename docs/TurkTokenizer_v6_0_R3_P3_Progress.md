# TurkTokenizer v6.0 R3-P3 progress

## Final boundary

R3-P3 is closed as `DROP_AFTER_SCREEN`. The R3 line is closed.

| Item | Final state |
|---|---|
| v1 masked-training run | Protocol-invalid after Relation E01; E02 did not run |
| v1 result status | Diagnostic only; promotion decision forbidden |
| v2 method | Completed R1 protected state plus 123 R3-P2 direct-family tensors |
| Optimizer steps | 0 |
| Parent reproduction / graft smoke / start gate | PASS / PASS / PASS |
| Macro relation F1 | 0.7795 |
| Minimum-family F1 | 0.7139 (OBJECT) |
| POSS_HEAD / OBJECT | 0.7594 / 0.7139 |
| PARTICIPLE_HEAD / CASE_GOVERNOR | 0.7628 / 0.8820 |
| UAS / LAS | 0.8831 / 0.7643 |
| Gates | 3 / 12 passed |
| Decision | DROP_AFTER_SCREEN |
| Final A/B closure packages | Re-materialized and checksum-verified |
| Sealed evaluation | unopened |

The three passing gates were the protected `CASE_GOVERNOR`, UAS, and LAS
regression limits; all three metrics equal R1 exactly. The nine direct-family,
aggregate, factorized OBJECT, and matched-control gates failed. Relative to
R3-P2, macro F1 fell by `0.0346`, POSS_HEAD by `0.0675`,
PARTICIPLE_HEAD by `0.0718`, OBJECT by `0.0108`, and micro direct head
top-1 by `0.0099`.

The scientific conclusion is that R3-P2's ranking gain is jointly encoded in
the shared representation and calibration. It is not transferable as a
standalone direct-family scorer graft. Post-hoc rescue is closed.

See [the corrected v2 precommit](TurkTokenizer_v6_0_R3_P3_v2_Precommit.md),
[the final decision](TurkTokenizer_v6_0_R3_P3_Decision.md), and
[the draft R4 plan](TurkTokenizer_v6_1_R4_Plan.md).
