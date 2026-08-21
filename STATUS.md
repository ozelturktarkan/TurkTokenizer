# Project status — 2026-08-21

## Reliable state

- v3S is closed and rejected before `INTERNAL_VAL`.
- Locked v4 and hard-negative recovery are closed and rejected before `INTERNAL_VAL`.
- v4.1 A1 is retained as a finalist candidate, but it did not pass the absolute CALIB gates.
- v4.1 A2 is dropped after its single-seed screen.
- v4.1 A3 passed its TRAIN-only coverage and smoke gates.
- A3 neural screening is incomplete. The interrupted run has no valid final screen decision.
- `INTERNAL_VAL_CONSUMED = false`.
- External BOUN/IMST/Penn holdouts and official TEST splits remain unopened.

## A3 coverage evidence

- Corrected joint lemma + mapped morphology recall at top 20: `0.9632123329812057` (gate: `>=0.95`).
- Minimum relation-critical requirement candidate recall at top 20: `0.9573986804901037` (gate: `>=0.95`).
- Gold/oracle-note violations: none.
- Lattice surfaces: `46,519`; maximum candidates: `20`; empty lists: `0`.
- Smoke architecture: 8 Transformer layers, 8 heads, hidden size 384, 28,848,978 parameters, finite gradients.

## Interrupted A3 run

The run used seed `51104` with the locked TRAIN/CALIB resources and kept the sealed internal-validation resource unread.

- Best complete syntax checkpoint: epoch 11 (`UAS=0.8693`, `LAS=0.7458`, `UPOS=0.9085`).
- Last complete relation evaluation: epoch 3 (`macro=0.7860`, `minimum/OBJECT=0.7019`, `UAS=0.8705`, `LAS=0.7434`).
- Relation epoch 4 was computing when the workspace was interrupted.
- Hard-negative mining did not begin.
- No final A3 CALIB audit, gate, frozen checkpoint, or screen result exists.

The safe continuation is a clean A3 restart with epoch-level durable state and periodic off-workspace checkpoint synchronization. Scores from the interrupted partial run must not be promoted or filled in by inference.
