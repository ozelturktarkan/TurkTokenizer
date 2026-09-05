# TurkTokenizer v6.1 R4 planning note

> Status: ACTIVE — R4-P0 passed; R4-P1 finalized as `DROP_AFTER_SCREEN` with a reproducible fresh focal parent; R4-P2 precommit pending.

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

R4-P0 fixed the P2 adapter boundary at post-graph/pre-family scoring with
bottleneck width 48, LayerNorm plus GELU, residual-gate initial logit `-2.0`,
and at most 200,000 new parameters. PCGrad is fixed for the shared Transformer,
relation bridge, and syntax bridge under the deterministic task order recorded
in the P0 precommit. P1 may not use either mechanism.

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

## R4-P0 outcome

R4-P0 passed all integrity conditions on 12 deterministic TRAIN batches with
zero optimizer steps, unchanged model state, and no CALIB access. It fixed the
routing and adapter boundary described above. R4-P1 must now lock fresh-training
ceilings, patience, overfitting guards, screen gates, and A/B persistence before
its first optimizer step.

## R4-P1 outcome

R4-P1 completed the fresh repaired-lattice reconstruction without adapter, PCGrad, ranking loss, or checkpoint migration. Syntax E24, Relation E22, and Hard-Negative H03 were the selected checkpoints at their respective completed stage boundaries. The unchanged H03 checkpoint was screened twice independently; all final screen outputs matched exactly, and a separate CPU recomputation reproduced the result.

| Metric | R4-P1 | R4 planning gate | Result |
|---|---:|---:|---|
| Macro relation F1 | 0.813891 | >= 0.814142 | Miss |
| Minimum-family F1 | 0.712152 | >= 0.724658 | Miss |
| OBJECT F1 | 0.712152 | > 0.724658 | Miss |
| POSS_HEAD F1 | 0.813253 | >= 0.816991 | Miss |
| PARTICIPLE_HEAD F1 | 0.841270 | >= 0.835438 | Pass |
| CASE_GOVERNOR F1 | 0.888889 | >= 0.880029 | Pass |
| UAS | 0.885210 | >= 0.881053 | Pass |
| LAS | 0.763815 | >= 0.762309 | Pass |
| OBJECT source F1 | 0.726993 | >= 0.723857 | Pass |
| OBJECT conditional head top-1 | 0.927934 | >= 0.934739 | Miss |
| Micro direct head top-1 | 0.931490 | > 0.940570 | Miss |

The precommitted P1 screen decision is `DROP_AFTER_SCREEN`: macro gain over A1 was only `+0.00313462`, below the required `+0.01`, and minimum-family F1 changed by `-0.00525455`. This does not invalidate P1's parent-reconstruction role. Its final closure is retained in two independently re-materialized 37-file private packages with all manifest checksums, byte equality, and reconstructed state verified.

The result sharpens the P2 question. OBJECT source detection already clears its planning floor, whereas exact OBJECT and conditional/micro head ranking do not. PARTICIPLE_HEAD, CASE_GOVERNOR, UAS, and LAS are already above their protected floors. R4-P2 should therefore test only the fixed P0 adapter and PCGrad isolation design under the unchanged focal objective. Ranking loss remains reserved for P3. R4-P2 has not started; its paired-control rule, full overfitting guards, schedule, and persistence contract must be signed before any optimizer step. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.
