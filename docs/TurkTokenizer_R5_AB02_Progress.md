# TurkTokenizer R5 AB02-A progress

Independent experiment: original AB00/M0 v0.7.0 hybrid plus a candidate-local averaged perceptron. AB01 is absent; this line is separate from v6/R4.

Status: training complete. No model promotion.

TRAIN: 3,278 IMST r2.15 TRAIN sentences, 22,878 eligible words, 384,254 TRAIN-only features. CALIB: 128 BOUN r2.15 TRAIN sentences, 1,120 non-punctuation reference words. Official DEV/TEST was not opened.

The original M0 and zero-score equivalence checks passed. Seeds and stopping rules were fixed before training: seeds 17/29/43, primary seed 17, learning rate 0.1, ceiling 50, patience 5, earliest strict CALIB preferred-count improvement wins.

| Seed | Epochs run | Selected epoch | CALIB preferred hits | Correct selected | Wrong selected | Abstained/missing |
|---|---:|---:|---:|---:|---:|---:|
| M0 | 0 | 0 | 562 | 448 | 267 | 405 |
| 17 | 15 | 10 | 701 | 610 | 215 | 295 |
| 29 | 20 | 15 | 702 | 625 | 218 | 277 |
| 43 | 22 | 17 | 703 | 613 | 218 | 289 |

These CALIB counts use the registered canonical native-role/declared-feature mapping; they are not official UD test results. BOUN original document IDs were unavailable, so document independence is not claimed.

Initial artifacts and all 57 epoch checkpoints have two durable copies. Models, data, source identifiers and private hashes are excluded from this public draft. No final evaluation metrics are included.

## AB02-J1 v0.2.0 — controlled improvement

Registration snapshot: preparation complete; recorded before training.

Only the training candidate bias changes: replace local M0 unary bias with fixed M0 sentence-conditional max-marginal scores, normalized per token. This introduces M0 ngram/partial-relation context into the local training comparison. It is not full structured training. Inference, feature vocabulary, candidate IDs, morphology, update rule, hyperparameters and 2.5 margin are unchanged. AB01 and CRF are absent.

The same 22,878 supervised words and exact target/feature IDs are retained. Relative training bias changes in 14,432 words. Seeds 17/29/43 train from zero; CALIB and stopping rules remain fixed. An additional 128 BOUN TRAIN sentences unused in AB02-v0.1 are reserved for post-selection checking; no document-level or project-wide unseen claim is made.

## v0.2.0 current training status

Training in progress; round 1 has durable A/B checkpoints.

Only aggregate TRAIN/CALIB metrics follow. CALIB preferred-count controls epoch selection; ties retain the earliest epoch. Patience is 5.

| Round | Seed | Epoch | TRAIN updates | CALIB preferred | Correct selected | Wrong selected | Abstained/missing | Best epoch | Patience | State |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 17 | 1 | 3364 | 726 | 642 | 197 | 281 | 1 | 0/5 | active |
| 1 | 29 | 1 | 3400 | 725 | 638 | 198 | 284 | 1 | 0/5 | active |
| 1 | 43 | 1 | 3355 | 729 | 639 | 199 | 282 | 1 | 0/5 | active |
