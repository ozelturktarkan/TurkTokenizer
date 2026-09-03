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

The two failed precommitted gates were:

- `CASE_GOVERNOR` regression limit
- `PARTICIPLE_HEAD` regression limit

The precommitted decision is `DROP_AFTER_SCREEN`. Promotion required every gate
to pass, so the two absolute family-regression failures prohibit post-hoc
rescue. Detailed CALIB metrics and private integrity hashes remain in the
private closure packages.

Two independent paired-decision executions, one from each verified control
closure package, produced byte-identical results. Candidate-arm and paired-
decision artifacts were each verified in two independent persistent packages.
`INTERNAL_VAL`, official TEST, and external holdouts remain unopened.
