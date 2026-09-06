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

Training in progress; round 10 has durable A/B checkpoints.

Only aggregate TRAIN/CALIB metrics follow. CALIB preferred-count controls epoch selection; ties retain the earliest epoch. Patience is 5.

| Round | Seed | Epoch | TRAIN updates | CALIB preferred | Correct selected | Wrong selected | Abstained/missing | Best epoch | Patience | State |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 17 | 1 | 3364 | 726 | 642 | 197 | 281 | 1 | 0/5 | active |
| 1 | 29 | 1 | 3400 | 725 | 638 | 198 | 284 | 1 | 0/5 | active |
| 1 | 43 | 1 | 3355 | 729 | 639 | 199 | 282 | 1 | 0/5 | active |
| 2 | 17 | 2 | 2109 | 731 | 654 | 197 | 269 | 2 | 0/5 | active |
| 2 | 29 | 2 | 2086 | 731 | 645 | 203 | 272 | 2 | 0/5 | active |
| 2 | 43 | 2 | 2143 | 737 | 657 | 204 | 259 | 2 | 0/5 | active |
| 3 | 17 | 3 | 1655 | 731 | 662 | 202 | 256 | 2 | 1/5 | active |
| 3 | 29 | 3 | 1625 | 729 | 658 | 202 | 260 | 2 | 1/5 | active |
| 3 | 43 | 3 | 1634 | 736 | 667 | 207 | 246 | 2 | 1/5 | active |
| 4 | 17 | 4 | 1306 | 728 | 662 | 205 | 253 | 2 | 2/5 | active |
| 4 | 29 | 4 | 1312 | 731 | 665 | 206 | 249 | 2 | 2/5 | active |
| 4 | 43 | 4 | 1310 | 737 | 672 | 209 | 239 | 2 | 2/5 | active |
| 5 | 17 | 5 | 1041 | 731 | 664 | 207 | 249 | 2 | 3/5 | active |
| 5 | 29 | 5 | 1085 | 731 | 668 | 205 | 247 | 2 | 3/5 | active |
| 5 | 43 | 5 | 1039 | 738 | 673 | 208 | 239 | 5 | 0/5 | active |
| 6 | 17 | 6 | 894 | 733 | 669 | 204 | 247 | 6 | 0/5 | active |
| 6 | 29 | 6 | 892 | 731 | 668 | 206 | 246 | 2 | 4/5 | active |
| 6 | 43 | 6 | 889 | 733 | 669 | 212 | 239 | 5 | 1/5 | active |
| 7 | 17 | 7 | 808 | 733 | 669 | 206 | 245 | 6 | 1/5 | active |
| 7 | 29 | 7 | 785 | 731 | 671 | 208 | 241 | 2 | 5/5 | complete |
| 7 | 43 | 7 | 769 | 731 | 671 | 213 | 236 | 5 | 2/5 | active |
| 8 | 17 | 8 | 705 | 734 | 671 | 209 | 240 | 8 | 0/5 | active |
| 8 | 43 | 8 | 693 | 735 | 673 | 213 | 234 | 5 | 3/5 | active |
| 9 | 17 | 9 | 607 | 735 | 670 | 209 | 241 | 9 | 0/5 | active |
| 9 | 43 | 9 | 595 | 736 | 674 | 214 | 232 | 5 | 4/5 | active |
| 10 | 17 | 10 | 536 | 734 | 670 | 213 | 237 | 9 | 1/5 | active |
| 10 | 43 | 10 | 571 | 735 | 677 | 213 | 230 | 5 | 5/5 | complete |
