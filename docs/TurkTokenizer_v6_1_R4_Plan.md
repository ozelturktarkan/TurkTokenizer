# TurkTokenizer v6.1 R4 planning note

> Status: DRAFT — not a precommit and not authorization to start training.

## Objective

R4 is a new mainline synthesis, not a checkpoint merge. Its target is to learn
the shared representation that made R3-P2's ranking loss effective while
preventing the CASE_GOVERNOR, PARTICIPLE_HEAD, and syntax regressions that
blocked promotion.

The repaired morphology lattice must be present from initialization and syntax
must be trained fresh. No R2-P9 E28, R1, or R3 checkpoint will be migrated into
the R4 model.

## Evidence carried forward

- A3 showed that top-20 morphology coverage was not the main OBJECT bottleneck;
  source-token detection remained weak while conditional head ranking was
  already strong.
- R3-P1 showed that source-only post-hoc activation reduces exact OBJECT edges.
- R3-P2 showed that ranking-oriented training can improve macro, OBJECT, minimum
  family, UAS, and LAS, but shared training can regress CASE_GOVERNOR and
  PARTICIPLE_HEAD.
- R3-P3 showed that copying the trained direct-family scorers onto R1 preserves
  protected metrics exactly but loses the ranking gains. The useful signal is
  representation- and calibration-entangled.

## Proposed staged program

| Phase | Single question | Locked change | Exit condition |
|---|---|---|---|
| R4-P0 | Where do family gradients conflict? | TRAIN-only gradient-cosine and module-attribution audit; no parameter update | Fixed routing map and adapter placement written before training |
| R4-P1 | Can the repaired-lattice R1 architecture be rebuilt cleanly from scratch? | Fresh initialization and fresh syntax training on the repaired lattice; existing focal objective | Reproducible parent plus A/B checkpoints; no architecture novelty |
| R4-P2 | Can family interference be reduced without ranking loss? | Add bounded family-specific residual adapters and explicit gradient routing; focal objective unchanged | Candidate beats paired P1 control with all protected-family gates intact |
| R4-P3 | Does ranking help after isolation exists? | From the same P2 syntax parent, paired focal-control versus zero-margin ranking candidate | Candidate passes every absolute and paired gate |
| R4-P4 | Is the result seed-stable? | Repeat the locked winner on three precommitted seeds | All seeds pass safety floors; aggregate rule fixed before runs |

A failed phase closes that phase. It does not permit threshold rescue or the
simultaneous addition of another mechanism. Only a passed phase may become the
parent of the next one.

## Architecture boundary

R4-P2 may add only small family-specific residual adapters at predeclared
relation-head inputs and a deterministic gradient-routing policy derived from
R4-P0. The shared encoder remains common. CASE_GOVERNOR gets its own adapter and
its loss may not update direct-family adapters; direct-family losses may not
update the CASE adapter. Any shared-trunk gradient surgery must be one named,
fixed algorithm with no tuned margin or temperature.

Candidate widths, insertion points, routing ownership, parameter budget, and
optimizer groups must be fixed in the eventual R4-P2 precommit. They are open
planning decisions today.

## Proposed promotion gates

The final R4 candidate should have to dominate the strongest useful evidence,
not merely the weakest baseline:

- macro relation F1 `>= 0.814142`;
- minimum-family F1 `>= 0.724658`;
- OBJECT F1 strictly above `0.724658`;
- POSS_HEAD F1 `>= 0.816991` (A1 minus 0.002);
- PARTICIPLE_HEAD F1 `>= 0.835438` (A1 minus 0.002);
- CASE_GOVERNOR F1 `>= 0.880029` (R1 minus 0.002);
- UAS `>= 0.881053` and LAS `>= 0.762309` (R1 minus 0.002);
- OBJECT source F1 `>= 0.723857`;
- OBJECT conditional head top-1 `>= 0.934739`;
- micro direct head top-1 strictly above `0.940570`;
- improvement over the matched focal control under the locked paired rule;
- zero sealed-data access before every CALIB gate and seed-stability condition
  passes.

The numeric gates are planning defaults and become binding only when copied
unchanged into a signed R4 precommit before execution.

## Data and evaluation contract

- TRAIN supplies gradients and R4-P0 diagnostics.
- CALIB supplies checkpoint selection and architecture screening.
- Threshold grids, early stopping, ceilings, patience, LR reductions, and
  aggregate multi-seed decision rules are precommitted before their first use.
- `INTERNAL_VAL` opens only if the final candidate passes every locked CALIB
  and multi-seed gate.
- Official TEST and external BOUN/IMST/Penn holdouts remain sealed under the
  existing Phase-5 policy.
- The suffix/allomorph registry remains a separate R5 research line and is not
  folded into R4.

## Decisions required before R4-P0 becomes a precommit

1. Choose the exact gradient-conflict statistic and sample budget.
2. Fix adapter insertion points and maximum parameter budget.
3. Select one gradient-routing algorithm or a simpler stop-gradient ownership
   map.
4. Define the three seed values and the multi-seed pass rule.
5. Set fresh-training ceilings, patience, and overfitting guards.
6. Specify A/B persistence and independent-decision reproduction requirements.

Until those decisions are locked, R4 remains planning-only.
