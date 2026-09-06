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

Training complete; all seed checkpoint choices are frozen. No automatic promotion.

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
| 11 | 17 | 11 | 505 | 733 | 672 | 213 | 235 | 9 | 2/5 | active |
| 12 | 17 | 12 | 484 | 732 | 675 | 213 | 232 | 9 | 3/5 | active |
| 13 | 17 | 13 | 462 | 734 | 676 | 213 | 231 | 9 | 4/5 | active |
| 14 | 17 | 14 | 443 | 735 | 676 | 214 | 230 | 9 | 5/5 | complete |

## v0.2.0 closure

Training and the registered comparisons are complete. The primary seed remains 17. The experiment is retained for analysis; promotion criteria were not all satisfied. No default-model promotion was made. No evaluation metrics or examples are published here.

Selected checkpoint CALIB values:

| Seed | Epochs run | Selected epoch | Preferred hits /1120 | Correct selected | Wrong selected | Abstained/missing |
|---|---:|---:|---:|---:|---:|---:|
| 17 | 14 | 9 | 735 | 670 | 209 | 241 |
| 29 | 7 | 2 | 731 | 645 | 203 | 272 |
| 43 | 10 | 5 | 738 | 673 | 208 | 239 |

All 31 completed epoch states have durable A/B copies. Each completed training round was recorded in this log before advancing. The final report retains matched-parent comparisons, decision transitions, and limitations. The remaining research question is how to preserve lexical/relational distinctions while improving confidence and joint decisions; changing a global threshold alone cannot change an incorrect first-ranked candidate.


## AB02 v0.3.0 — independent T1 and J2 experiments

AB03 remains unopened. This iteration studies two separate causes of AB02 errors.

- **T1 threshold-only:** fixed v0.2 models, a common threshold selected on reused CALIB only. Maximize pooled correct selections while never increasing any seed's wrong selections relative to 2.5; deterministic ties. The registered grid retained **2.5**, so T1 makes no runtime change. CALIB is development data.
- **J2 partial-label structured learning:** fresh averaged perceptrons using the same native feature vocabulary, candidates, targets and production decoder. Each update compares the current shared sentence path with the best partially labeled compatible path inside the same retained configurations. Relations and unlabeled tokens remain latent. Scope and plan inventories are cached; current-score configuration ranking is recomputed.
- TRAIN: 3,278 references, 22,878 eligible token targets, 384,254 frozen feature IDs. One averaging clock and at most one counted feature update per reference. No gold candidate injection or new linguistic rules.
- Seeds 17 / 29 / 43; primary 17 fixed; zero initialization, learning rate 0.1, 50-epoch ceiling, patience 5, earliest CALIB preferred-hit maximum including epoch 0. J2 margin remains 2.5.
- A new 128-sentence BOUN TRAIN check is frozen before model selection, excluding prior AB02 material and full IMST TRAIN under the existing duplicate policy. It is not claimed to be project-wide unseen or document-independent.
- Technical gates passed: independent tiny-lattice oracle, equivalence to native current-score sentence decoding, target-domain filtering before tag grouping, repeated-feature update counts, averaging and serialization checks.
- Initial and per-epoch A/B durable checkpoints precede advancement; each completed round is recorded here. Public reporting remains aggregate TRAIN/CALIB and work status only.
- No claim of complete syntactic search, exact Zemberek replication or perfect contextual accuracy. No automatic model promotion.

### J2 training rounds

| Round | Seed | Epoch | TRAIN document updates | CALIB preferred / 1120 | CALIB correct selected | CALIB wrong selected | Best epoch | Stopped |
|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 17 | 1 | 1731 | 729 | 628 | 193 | 1 | no |
| 1 | 29 | 1 | 1765 | 729 | 630 | 195 | 1 | no |
| 1 | 43 | 1 | 1749 | 726 | 635 | 198 | 1 | no |
| 2 | 17 | 2 | 1263 | 729 | 647 | 202 | 1 | no |
| 2 | 29 | 2 | 1308 | 739 | 650 | 201 | 2 | no |
| 2 | 43 | 2 | 1329 | 730 | 654 | 202 | 2 | no |
| 3 | 17 | 3 | 1043 | 733 | 659 | 208 | 3 | no |
| 3 | 29 | 3 | 1026 | 742 | 657 | 206 | 3 | no |
| 3 | 43 | 3 | 1076 | 734 | 662 | 206 | 3 | no |
| 4 | 17 | 4 | 843 | 740 | 659 | 207 | 4 | no |
| 4 | 29 | 4 | 885 | 743 | 662 | 206 | 4 | no |
| 4 | 43 | 4 | 854 | 737 | 663 | 203 | 4 | no |
| 5 | 17 | 5 | 760 | 740 | 661 | 208 | 4 | no |
| 5 | 29 | 5 | 768 | 744 | 665 | 204 | 5 | no |
| 5 | 43 | 5 | 722 | 737 | 665 | 204 | 4 | no |
| 6 | 17 | 6 | 641 | 739 | 659 | 208 | 4 | no |
| 6 | 29 | 6 | 661 | 744 | 669 | 202 | 5 | no |
| 6 | 43 | 6 | 651 | 740 | 668 | 209 | 6 | no |
| 7 | 17 | 7 | 557 | 738 | 659 | 208 | 4 | no |
| 7 | 29 | 7 | 558 | 744 | 669 | 205 | 5 | no |
| 7 | 43 | 7 | 599 | 743 | 670 | 208 | 7 | no |
| 8 | 17 | 8 | 479 | 735 | 660 | 210 | 4 | no |
| 8 | 29 | 8 | 515 | 742 | 669 | 205 | 5 | no |
| 8 | 43 | 8 | 483 | 742 | 670 | 210 | 7 | no |
| 9 | 17 | 9 | 489 | 737 | 665 | 210 | 4 | yes |
| 9 | 29 | 9 | 469 | 739 | 669 | 208 | 5 | no |
| 9 | 43 | 9 | 464 | 743 | 671 | 210 | 7 | no |
| 10 | 29 | 10 | 446 | 739 | 673 | 208 | 5 | yes |
| 10 | 43 | 10 | 471 | 742 | 669 | 210 | 7 | no |
| 11 | 43 | 11 | 413 | 741 | 671 | 209 | 7 | no |
| 12 | 43 | 12 | 390 | 739 | 672 | 209 | 7 | yes |


### v0.3.0 completion and decision

All three J2 runs stopped by the registered patience rule: 31 seed-epochs in total, with 62 distinct A/B checkpoint records and 12 published round groups. Model selection was frozen before the new check was scored.

| Seed | Epochs run | Selected epoch | Selected CALIB preferred / 1120 | Selected CALIB correct selected | Selected CALIB wrong selected |
|---:|---:|---:|---:|---:|---:|
| 17 | 9 | 4 | 740 | 659 | 207 |
| 29 | 10 | 5 | 744 | 665 | 204 |
| 43 | 12 | 7 | 743 | 670 | 208 |

The selected T1 threshold remained 2.5; its unchanged parent behavior was reproduced. J2 did not meet the preregistered replacement criteria and is retained as a documented experiment. AB00 stays the locked baseline; v0.2 stays the preceding AB02 comparison reference. Neither is being declared a perfect contextual analyzer.

Both arms and all seeds completed the word-regression, contextual-regression, prior diagnostic/transfer and newly frozen check runs. Native analyses and spans stayed identical; structural graph checks passed. Source, data, model checkpoints and the parent package passed integrity checks. Private evaluation outputs, examples, model weights and corpus material are excluded from this public log.

The next AB02 hypothesis is learnable transitions between selected adjacent lemma/native-group analyses, with an appropriate decoder state and an independent oracle check. Sparse supervision and the model-selection/commitment objective also need separate study. These are proposed follow-up experiments, not implemented changes. **AB03 remains unopened.**
