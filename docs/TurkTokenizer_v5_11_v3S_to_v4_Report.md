# v5.11-v3S CALIB Closure → v5.11-v4

## v3S
**REJECT BEFORE INTERNAL VAL.**

- best epoch: 8
- macro F1: 76.0606%
- minimum-family F1: 62.9067%
- internal VAL consumed: NO

Factorized bottleneck:
- OBJECT source F1: 68.9139%
- OBJECT head@1 given gold source: 89.6368%
- PARTICIPLE source F1: 82.1124%
- PARTICIPLE head@1 given gold source: 88.5185%
- CASE edge F1 given gold source: 98.1964%

This is an architectural failure, not a threshold-only failure.

## v4
Training corpus pool: **Kenet + Tourism + ATIS + FrameNet official TRAIN**.

Entire corpus-level external holdout: **BOUN + IMST + Penn official TRAIN**.

Backbone: 8-layer relative-position Transformer over raw/char/full frozen morphology lattice, with full dependency parsing, soft graph propagation, relation-specific experts and learned structural fusion.

Internal VAL remains sealed until CALIB reaches:
- macro relation F1 >= 90%
- minimum-family F1 >= 87%
- UAS >= 88%
- LAS >= 80%

Only after the internal architecture gate will the 3-corpus external Phase-5 gate be prepared/scored.
