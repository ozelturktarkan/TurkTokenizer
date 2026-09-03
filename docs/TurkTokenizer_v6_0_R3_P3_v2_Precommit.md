# TurkTokenizer v6.0 R3-P3 v2 precommit

## Question

Does the direct-family ranking signal learned by the R3-P2 candidate transfer onto
the completed R1 backbone without importing the candidate's shared or
`CASE_GOVERNOR` regressions?

This is a controlled R3 follow-up, not a synthesis release and not R4.

## Why v1 was stopped

The first R3-P3 design started masked training from the selected R1 Syntax E10
checkpoint. The mask itself was correct, but the starting boundary was not a
valid comparator for the frozen branches: relation and hard-negative training
had not yet produced R1's final protected `CASE_GOVERNOR` and syntax state.
After Relation E01 exposed that mismatch, the run was invalidated before E02.

The E01 numbers are protocol diagnostics only. They are not an R3-P3 result, no
promotion decision may be derived from them, and no post-hoc rescue is allowed.
The invalidation record and duplicate private packages are retained for audit.

## Corrected one-delta design

R3-P3 v2 performs a deterministic parameter graft:

- base: the completed, frozen R1 checkpoint;
- donor: the closed R3-P2 ranking-loss candidate;
- graft: exactly 123 existing tensors (2,222,643 parameters) belonging to the
  `POSS_HEAD`, `OBJECT`, and `PARTICIPLE_HEAD` direct-relation modules;
- protected state: 216 tensors (27,083,444 parameters), including the shared
  encoder, morphology and syntax paths, graph-message layers, and complete
  `CASE_GOVERNOR` path, copied from R1;
- optimization: zero training epochs and zero optimizer steps;
- data access before the screen: no CALIB deserialization during graft smoke.

No new parameters, features, losses, thresholds, or decoder rules are
introduced. The resulting checkpoint is evaluated once on CALIB.

## Locked checks

Before CALIB is opened, the implementation must establish all of the following:

1. R1 CALIB reproduction matches the archived R1 relation and syntax metrics.
2. Base and donor expose identical model-state keys.
3. Every graft tensor equals the R3-P2 donor bit-for-bit.
4. Every protected tensor equals the completed R1 base bit-for-bit.
5. All parameters are frozen.
6. The graft changes direct-family outputs in the TRAIN smoke batch.
7. Ten protected syntax and CASE output groups remain bit-identical.
8. The precommit, runner, smoke, start-gate record, and inputs exist in two
   independently materialized private packages with verified checksums.

These checks are complete and the start gate is `PASS`.

## Binding CALIB gates

The original twelve R3-P2 gates remain unchanged:

- `OBJECT >= 0.719407`
- macro F1 `>= 0.810756`
- minimum-family F1 `>= 0.719407`
- OBJECT conditional head top-1 `>= 0.934739`
- OBJECT source F1 `>= 0.723857`
- `POSS_HEAD` regression versus A1 `<= 0.002`
- `PARTICIPLE_HEAD` regression versus A1 `<= 0.002`
- `CASE_GOVERNOR` regression versus R1 `<= 0.002`
- UAS regression versus R1 `<= 0.002`
- LAS regression versus R1 `<= 0.002`
- OBJECT F1 must beat the R3-P2 matched control
- micro direct head top-1 must beat the R3-P2 matched control

All twelve must pass for promotion. Otherwise the decision is
`DROP_AFTER_SCREEN`. `INTERNAL_VAL`, official TEST, and external holdouts
remain sealed. R3 closes after this single decision; any synthesis architecture
belongs to the separately precommitted R4 line.
