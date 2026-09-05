# TurkTokenizer v6.1 R4-P2 matched focal control progress

> Status: ACTIVE — Relation E01 completed and independently archived; E02 pending.

## Purpose

This arm is the matched focal control for R4-P2. It starts Relation training fresh from the independently verified R4-P1 Syntax E24 parent and changes no learning mechanism relative to R4-P1. Its purpose is to establish the paired baseline against which the fixed R4-P0 adapter-plus-PCGrad candidate can later be judged.

## Locked control

- Seed: `51104`; batch size: `24`.
- Syntax parent: R4-P1 selected Syntax E24; relation sampler begins at the completed Syntax boundary, epoch `27`.
- Relation and Hard-Negative parameters are initialized fresh.
- The R4-P1 focal trainer and objective are reused unchanged.
- Family adapters: disabled.
- PCGrad: disabled.
- Ranking loss: disabled and reserved for R4-P3.
- Relation ceiling: E50; patience: `9`; initial learning rate: `0.00025`.
- Hard-Negative ceiling: H50; patience: `9`; initial learning rate: `0.00012`.
- A deterministic learning-rate halving applies at the fourth consecutive non-improving epoch.
- Hard-Negative penalty warmup is `0.10`, `0.15`, `0.20`, then `0.25`.
- Relation and Hard-Negative each use a symmetric `0/3` overfitting guard from their first epoch. A signal requires no selection improvement, falling TRAIN loss, and at least a 0.1% rise in gold-CALIB objective loss; three consecutive signals stop the stage safely.
- Final CALIB screening, if reached, will be executed twice unchanged and must agree exactly.
- Every completed epoch boundary must be retained in two independent private packages and re-read with all manifest checksums verified before the next epoch begins.

## Start-gate result

The precommit, architecture smoke test, and zero-step start gate passed. The verified start package contains 16 files, with all 15 manifest checksums passing in each of two independently re-materialized copies. The selected R4-P1 Syntax E24 parent, sampler boundary, fresh Relation/Hard-Negative state, and zero optimizer-step condition were all confirmed.

## Relation progress

| Epoch | TRAIN loss | Gold-CALIB objective loss | Macro F1 | Min/OBJECT F1 | UAS | LAS | Selection score | Patience | LR | Overfit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E01 | 0.5198 | 1.847522 | 0.791514 | 0.683742 | 0.874382 | 0.751460 | 0.766242 | 0/9 | 0.00025 | 0/3 baseline |

E01 was independently re-evaluated from its persisted state. Both 28-file private A/B packages were re-materialized; all 27 manifest checksums, source/A/B byte equality, the selected checkpoint, and reconstructed state passed. This freshly executed arm—not the historical P1 trajectory—is the locked paired control that the R4-P2 adapter-plus-PCGrad candidate must beat.

Relation E02 has not started at this public boundary. `INTERNAL_VAL`, external BOUN/IMST/Penn holdouts, and official TEST remain unopened.
