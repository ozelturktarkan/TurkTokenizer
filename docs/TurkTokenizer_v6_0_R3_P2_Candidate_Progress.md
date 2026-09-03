# TurkTokenizer v6.0 R3-P2 candidate progress

R3-P2 is a closed paired TRAIN/CALIB ablation. The candidate arm used the
precommitted zero-margin hardest-competitor logistic ranking direct-family loss
and restored the same precommitted R1 syntax parent checkpoint as the control arm.

| Candidate boundary | Integrity status |
| --- | --- |
| Relation E01 | Primary, local mirror, and persistent A/B packages verified |
| Relation E02 | Primary, local mirror, and persistent A/B packages verified |
| Relation E03 | Primary, local mirror, and persistent A/B packages verified |
| Relation E04 | Primary, local mirror, and persistent A/B packages verified |
| Relation E05 | Primary, local mirror, and persistent A/B packages verified |
| Relation E06 | Primary, local mirror, and persistent A/B packages verified |
| Relation E07 | Primary, local mirror, and persistent A/B packages verified |
| Relation E08 | Primary, local mirror, and persistent A/B packages verified |
| Relation E09 | Primary, local mirror, and persistent A/B packages verified |
| Relation E10 | Primary, local mirror, and persistent A/B packages verified |
| Relation E11 | Primary, local mirror, and persistent A/B packages verified |
| Relation E12 | Primary, local mirror, and persistent A/B packages verified |
| Relation E13 | Primary, local mirror, and persistent A/B packages verified |
| Relation E14 | Primary, local mirror, and persistent A/B packages verified |
| Relation E15 | Primary, local mirror, and persistent A/B packages verified |
| Relation E16 | Primary, local mirror, and persistent A/B packages verified |
| Relation E17 | Primary, local mirror, and persistent A/B packages verified |
| Relation E18 | Primary, local mirror, and persistent A/B packages verified |
| Relation E19 | Primary, local mirror, and persistent A/B packages verified |
| Relation E20 | Primary, local mirror, and persistent A/B packages verified |
| Relation E21 | Primary, local mirror, and persistent A/B packages verified |
| Relation E22 | Primary, local mirror, and persistent A/B packages verified |
| Relation E23 | Primary, local mirror, and persistent A/B packages verified |
| Relation E24 | Primary, local mirror, and persistent A/B packages verified |
| Relation E25 | Primary, local mirror, and persistent A/B packages verified |
| Relation E26 | Primary, local mirror, and persistent A/B packages verified |
| Relation E27 | Primary, local mirror, and persistent A/B packages verified |
| Relation E28 | Primary, local mirror, and persistent A/B packages verified |
| Relation E29 | Primary, local mirror, and persistent A/B packages verified |
| Relation E30 | Primary, local mirror, and persistent A/B packages verified |
| Relation E31 | Primary, local mirror, and persistent A/B packages verified |
| Relation E32 | Primary, local mirror, and persistent A/B packages verified |
| Relation E33 | Primary, local mirror, and persistent A/B packages verified |
| Relation E34 | Primary, local mirror, and persistent A/B packages verified |
| Relation E35 | Primary, local mirror, and persistent A/B packages verified |
| Relation E36 | Primary, local mirror, and persistent A/B packages verified |
| Relation E37 | Primary, local mirror, and persistent A/B packages verified |
| Relation E38 | Primary, local mirror, and persistent A/B packages verified |
| Relation E39 | Primary, local mirror, and persistent A/B packages verified |
| Relation E40 | Primary, local mirror, and persistent A/B packages verified |
| Relation E41 | Primary, local mirror, and persistent A/B packages verified |
| Relation E42 | Primary, local mirror, and persistent A/B packages verified |
| Relation E43 | Primary, local mirror, and persistent A/B packages verified |
| Relation E44 | Primary, local mirror, and persistent A/B packages verified |
| Relation E45 | Primary, local mirror, and persistent A/B packages verified |
| Relation E46 | Primary, local mirror, and persistent A/B packages verified |
| Relation E47 | Primary, local mirror, and persistent A/B packages verified |
| Relation E48 | Primary, local mirror, and persistent A/B packages verified |
| Relation E49 | Primary, local mirror, and persistent A/B packages verified |
| Relation E50 | Primary, local mirror, persistent A/B packages, selected checkpoint, and completion marker verified |
| Hard-Negative E01 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E02 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E03 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E04 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E05 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E06 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E07 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E08 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E09 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E10 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E11 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E12 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E13 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E14 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E15 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E16 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E17 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E18 | Primary, local mirror, fixed cache, selected checkpoint, and persistent A/B packages verified |
| Hard-Negative E19 | Primary, local mirror, fixed cache, selected checkpoint, completion marker, and persistent A/B packages verified |
| Candidate CALIB screen | Final model, calibration, audit, screen marker, active/durable mirror, and persistent A/B closure packages verified |
| Paired CALIB decision | Two byte-identical executions, 10/12 gates passed, `DROP_AFTER_SCREEN`, and persistent A/B decision packages verified |

The candidate Relation stage completed at E50. The selected checkpoint and
blinded Relation completion marker are verified in both persistent packages.
Candidate Hard-Negative completed at E19. Its fixed cache, selected checkpoint,
completion marker, active/durable state pair, and independent A/B closure
packages are verified. The candidate TRAIN/CALIB screen also completed; its
final artifacts and arm marker are verified in two independent persistent
closure packages. The paired decision passed 10 of 12 gates but missed the
absolute `CASE_GOVERNOR` and `PARTICIPLE_HEAD` regression limits, yielding
`DROP_AFTER_SCREEN`. Two independent decision executions and persistent A/B
decision packages were verified.

No control or candidate CALIB metric was published or inspected before both arms
closed. INTERNAL_VAL, official TEST, and external holdouts remain unopened. See
[the R3-P2 decision](TurkTokenizer_v6_0_R3_P2_Decision.md).
