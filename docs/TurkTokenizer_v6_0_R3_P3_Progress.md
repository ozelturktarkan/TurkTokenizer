# TurkTokenizer v6.0 R3-P3 progress

## Current boundary

R3-P3 is precommitted as a one-delta family-isolation experiment. Candidate training has not started.

| Item | State |
|---|---|
| Runtime bridge | PASS; archived R3-P2 candidate Relation E01 reproduced byte-for-byte |
| Parameter-mask smoke | PASS |
| Start gate | PASS |
| Trainable parameters | 2,222,643 / 29,306,087 |
| Protected output groups | 10 / 10 bit-identical after the smoke update |
| Next stage | Relation E01 |
| Relation ceiling / patience | E50 / 9 |
| Hard-Negative ceiling / patience | E50 / 9 |
| Sealed evaluation | unopened |

The sole change from the R3-P2 candidate is the trainable-parameter mask. Each verified epoch boundary will be recorded here only after its primary/mirror state and two independent persistent packages are complete.
