# TurkTokenizer v6.0 R3-P2 decision

R3-P2 tested one paired TRAIN/CALIB change: the matched candidate replaced the
control arm's direct-family joint focal likelihood with the precommitted
zero-margin hardest-competitor logistic ranking loss. The parent syntax model,
decoder, inference rule, data, seed, runtime fingerprint, ceilings, and early
stopping policy were held fixed.

## Result

The candidate passed 10 of 12 precommitted gates. It improved on the matched
control for both required direct-family comparison gates and cleared the other
absolute aggregate, source/head, syntax, and POSS_HEAD gates.

| Aggregate CALIB metric | Matched control | Ranking-loss candidate | Delta |
|---|---:|---:|---:|
| Macro relation F1 | 0.8038 | 0.8141 | +0.0104 |
| Minimum-family F1 | 0.7218 | 0.7247 | +0.0028 |
| UAS | 0.8823 | 0.8868 | +0.0045 |
| LAS | 0.7640 | 0.7678 | +0.0038 |

The two failed precommitted gates were:

- `CASE_GOVERNOR` regression limit
- `PARTICIPLE_HEAD` regression limit

The precommitted decision is `DROP_AFTER_SCREEN`. Promotion required every gate
to pass, so the two absolute family-regression failures prohibit post-hoc
rescue. Detailed per-family diagnostics and private integrity hashes remain in
the private closure packages.

Two independent paired-decision executions, one from each verified control
closure package, produced byte-identical results. Candidate-arm and paired-
decision artifacts were each verified in two independent persistent packages.
`INTERNAL_VAL`, official TEST, and external holdouts remain unopened.
