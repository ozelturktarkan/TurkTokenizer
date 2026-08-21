# Project status — 2026-08-21

## Reliable state

- v3S is closed and rejected before `INTERNAL_VAL`.
- Locked v4 and hard-negative recovery are closed and rejected before `INTERNAL_VAL`.
- v4.1 A1 is retained as a finalist candidate, but it did not pass the absolute CALIB gates.
- v4.1 A2 is dropped after its single-seed screen.
- v4.1 A3 passed its TRAIN-only coverage and architecture smoke gates.
- The earlier interrupted A3 run is superseded by a clean, resumable restart.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.

## A3 coverage evidence

- Corrected joint lemma + mapped morphology recall at top 20: `0.9632123329812057` (gate: `>=0.95`).
- Minimum relation-critical requirement candidate recall at top 20: `0.9573986804901037` (gate: `>=0.95`).
- Gold/oracle-note violations: none.
- Lattice surfaces: `46,519`; maximum candidates: `20`; empty lists: `0`.
- Smoke architecture: 8 Transformer layers, 8 heads, hidden size 384, 28,848,978 parameters, finite gradients.

## Resumable A3 restart

The clean restart uses seed `51104`, the locked TRAIN/CALIB resources, epoch-level optimizer/RNG/sampler continuation state, and periodic off-workspace checkpoint synchronization. The sealed internal-validation resource remains unread.

Syntax training completed all 12 planned epochs. The selected checkpoint is epoch 11 under the precommitted score `0.60·LAS + 0.30·UAS + 0.10·UPOS`:

- `UAS=0.8675`
- `LAS=0.7436`
- `UPOS=0.9125`
- selection score: approximately `0.79766`

Relation training is now in progress. No final A3 CALIB audit, gate decision, frozen checkpoint, or screen result exists yet; partial scores must not be promoted as a final result.
