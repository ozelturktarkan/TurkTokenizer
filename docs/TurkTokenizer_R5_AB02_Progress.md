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


## AB02 v0.4.0 — J3 learned adjacent lemma/native-group transitions

AB03 remains unopened. J3 adds first-order learned transitions between adjacent selected analyses to the previous J2 partial-label structured learner. The causal control is frozen J2; v0.2 remains the preceding AB02 reference. Neither predecessor is newly promoted.

- Six registered feature families: POS pair; last-to-first native group; full native group paths; lemma/POS pair; left lemma with right groups; left groups with right lemma. Native groups are not claimed identical to Zemberek IG.
- TRAIN-only feature inventory from raw candidate cross-products, with each feature supported by at least two distinct adjacent positions (alternatives within a position are deduplicated). **81,068** new IDs follow **384,254** unchanged unary IDs.
- The exact inner DP retains the previous native tag and current native tag+lemma+groups. Same-tag lexical alternatives remain separate. Candidate max-marginals use forward/backward inference. Existing token order, punctuation, BOS/EOS and hard blocks remain explicit; no skip edges or distant-context module.
- Native morphology, original candidates, 3,278 TRAIN references, 22,878 target sets, fixed n-gram/relation scores, outer planner and budgets stay unchanged. Outer configuration pruning continues to use native unary/relation priority; learned edges rescore the retained configurations. Outer search is still approximate.
- Fresh zero weights; seeds 17/29/43, primary17; learning rate0.1, one clock/update opportunity per reference, max50 epochs, patience5, earliest CALIB preferred-hit maximum including epoch0. Threshold2.5 unchanged.
- A new128-sentence BOUN TRAIN check is frozen before selection; all prior AB02 material and full IMST TRAIN excluded by the existing duplicate policy. No document-level/project-wide unseen claim; official DEV/TEST unopened.
- Implementation gates passed:160 brute-force best-path cases and1,680 candidate max-marginals; same-tag/different-lemma trap;128-sentence native J2 equivalence with zero edge weights;12 nonzero-score cached/live checks; counted edge updates; deterministic two-epoch serialization/resume.
- Initial and per-epoch durable A/B checkpoints precede advancement. Public log contains aggregate TRAIN/CALIB and status only.

### J3 training rounds

| Round | Seed | Epoch | TRAIN document updates | CALIB preferred /1120 | CALIB correct selected | CALIB wrong selected | Best epoch | Stopped |
|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 17 | 1 | 1747 | 726 | 641 | 196 | 1 | no |
| 1 | 29 | 1 | 1703 | 732 | 652 | 198 | 1 | no |
| 1 | 43 | 1 | 1714 | 730 | 643 | 200 | 1 | no |
| 2 | 17 | 2 | 1192 | 740 | 661 | 199 | 2 | no |
| 2 | 29 | 2 | 1242 | 737 | 671 | 205 | 2 | no |
| 2 | 43 | 2 | 1218 | 733 | 646 | 206 | 2 | no |
| 3 | 17 | 3 | 933 | 740 | 668 | 201 | 2 | no |
| 3 | 29 | 3 | 894 | 743 | 677 | 203 | 3 | no |
| 3 | 43 | 3 | 919 | 747 | 663 | 203 | 3 | no |
| 4 | 17 | 4 | 710 | 746 | 672 | 202 | 4 | no |
| 4 | 29 | 4 | 729 | 743 | 675 | 205 | 3 | no |
| 4 | 43 | 4 | 715 | 748 | 670 | 203 | 4 | no |
| 5 | 17 | 5 | 608 | 750 | 674 | 198 | 5 | no |
| 5 | 29 | 5 | 560 | 747 | 680 | 207 | 5 | no |
| 5 | 43 | 5 | 586 | 750 | 672 | 204 | 5 | no |
| 6 | 17 | 6 | 491 | 748 | 678 | 201 | 5 | no |
| 6 | 29 | 6 | 515 | 746 | 678 | 207 | 5 | no |
| 6 | 43 | 6 | 501 | 753 | 676 | 205 | 6 | no |
| 7 | 17 | 7 | 416 | 749 | 678 | 201 | 5 | no |
| 7 | 29 | 7 | 426 | 748 | 679 | 205 | 7 | no |
| 7 | 43 | 7 | 443 | 753 | 679 | 204 | 6 | no |
| 8 | 17 | 8 | 369 | 752 | 676 | 200 | 8 | no |
| 8 | 29 | 8 | 379 | 752 | 682 | 205 | 8 | no |
| 8 | 43 | 8 | 386 | 755 | 680 | 204 | 8 | no |
| 9 | 17 | 9 | 303 | 752 | 683 | 202 | 8 | no |
| 9 | 29 | 9 | 316 | 752 | 685 | 205 | 8 | no |
| 9 | 43 | 9 | 317 | 754 | 678 | 203 | 8 | no |
| 10 | 17 | 10 | 287 | 752 | 684 | 203 | 8 | no |
| 10 | 29 | 10 | 280 | 753 | 684 | 206 | 10 | no |
| 10 | 43 | 10 | 307 | 754 | 682 | 204 | 8 | no |
| 11 | 17 | 11 | 249 | 753 | 687 | 203 | 11 | no |
| 11 | 29 | 11 | 280 | 752 | 685 | 207 | 10 | no |
| 11 | 43 | 11 | 239 | 751 | 683 | 203 | 8 | no |
| 12 | 17 | 12 | 267 | 755 | 689 | 202 | 12 | no |
| 12 | 29 | 12 | 248 | 752 | 688 | 208 | 10 | no |
| 12 | 43 | 12 | 232 | 752 | 682 | 204 | 8 | no |
| 13 | 17 | 13 | 239 | 755 | 687 | 202 | 12 | no |
| 13 | 29 | 13 | 260 | 752 | 689 | 208 | 10 | no |
| 13 | 43 | 13 | 240 | 754 | 679 | 205 | 8 | yes |
| 14 | 17 | 14 | 223 | 755 | 690 | 202 | 12 | no |
| 14 | 29 | 14 | 236 | 750 | 688 | 208 | 10 | no |
| 15 | 17 | 15 | 210 | 754 | 692 | 205 | 12 | no |
| 15 | 29 | 15 | 228 | 751 | 688 | 209 | 10 | yes |
| 16 | 17 | 16 | 194 | 754 | 689 | 204 | 12 | no |
| 17 | 17 | 17 | 195 | 754 | 689 | 204 | 12 | yes |


### v0.4.0 completion and decision

All J3 runs stopped under the registered patience rule. The 45 completed seed-epochs have 90 distinct durable A/B checkpoint records and 17 published round groups. Selected models were locked before the new check was scored.

| Seed | Epochs run | Selected epoch | Selected CALIB preferred /1120 | Selected CALIB correct selected | Selected CALIB wrong selected |
|---:|---:|---:|---:|---:|---:|
| 17 | 17 | 12 | 755 | 689 | 202 |
| 29 | 15 | 10 | 753 | 684 | 206 |
| 43 | 13 | 8 | 755 | 680 | 204 |

J3 completed every registered word/context, prior diagnostic/transfer and fresh-check evaluation for all three seeds. It did **not** satisfy the registered replacement criteria and is not promoted. AB00 remains the locked baseline and v0.2 remains the prior AB02 comparison reference.

A post-selection diagnostic also turned off only learned edges while retaining selected J3 unary weights on already observed probes. It demonstrated that the added transitions affect inference in both helpful and harmful ways; it was not used to choose or promote a model. Separate retrained feature-family ablations and a balanced development/calibration design are proposed next steps, not implemented follow-ups.

Native analyses, boundaries and token positions passed equivalence checks. All source/data/evaluation freezes, initial package members, parent package members and epoch checkpoint state/metric hashes passed integrity verification. Code, selected models, detailed results and reusable diagnostics are retained in the experiment package. This public log continues to exclude evaluation examples/results, corpus material and model weights.

**AB03 remains unopened.**


## AB02 v0.5.0 — final controlled J4 study

Registered before J4 training or new development scoring. AB03 remains unopened.

- Retrain two disjoint feature-family ablations from zero: **M** uses POS/native-group transitions (34,073 IDs); **L** uses lemma-containing transitions (46,995 IDs). Full frozen J3 is the matched-protocol control. All 384,254 unary IDs, 3,278 TRAIN references and 22,878 supervised targets remain unchanged.
- Same seeds17/29/43, primary17; learning rate0.1, per-reference structured averaging clock, ceiling50, patience5, earliest original CALIB preferred maximum including epoch0. Raw analyses, morphology, ngram/relation weights and planner are unchanged.
- A separate balanced development set has128 BOUN TRAIN sentences (32 per bio/ess/news/pop),1,302 non-punctuation words. It is used only after epoch models are locked to select one common arm/threshold across all seeds. Each seed must preserve v0.2 preferred/correct counts and not increase wrong selections; otherwise retain v0.2 at2.5. Grid:1.5,2,2.5,3,3.5,4,4.5,5,6,8. Deterministic ties and conservative fallback are preregistered.
- A separate new128-sentence check is frozen before training and will only be scored after arm/threshold locking. Prior AB02 material through v0.4 and full IMST TRAIN are excluded by the existing duplicate policy. No official DEV/TEST, original-document independence or perfect-accuracy claim.
- Implementation checks passed: existing exact-inner-decoder oracle and zero-edge equivalence; complete disjoint family partition; all3,278 training records preserved per arm except filtered edge IDs;24 cached/live and counted-feature oracle cases; both arms serialize/resume deterministically and cannot update excluded edge IDs.
- Initial and per-epoch durable A/B checkpoints precede advancement; each completed round is recorded here. Public reporting remains aggregate TRAIN/CALIB and work status only. No automatic promotion.

### J4 training rounds

| Round | Arm | Seed | Epoch | TRAIN document updates | CALIB preferred /1120 | Correct selected | Wrong selected | Best epoch | Stopped |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | M | 17 | 1 | 1738 | 728 | 637 | 196 | 1 | no |
| 1 | M | 29 | 1 | 1727 | 733 | 643 | 198 | 1 | no |
| 1 | M | 43 | 1 | 1709 | 727 | 652 | 193 | 1 | no |
| 1 | L | 17 | 1 | 1737 | 726 | 636 | 198 | 1 | no |
| 1 | L | 29 | 1 | 1735 | 729 | 638 | 192 | 1 | no |
| 1 | L | 43 | 1 | 1715 | 727 | 631 | 200 | 1 | no |
| 2 | M | 17 | 2 | 1207 | 740 | 662 | 204 | 2 | no |
| 2 | M | 29 | 2 | 1256 | 736 | 660 | 205 | 2 | no |
| 2 | M | 43 | 2 | 1244 | 735 | 661 | 198 | 2 | no |
| 2 | L | 17 | 2 | 1195 | 729 | 646 | 201 | 2 | no |
| 2 | L | 29 | 2 | 1244 | 733 | 656 | 194 | 2 | no |
| 2 | L | 43 | 2 | 1250 | 735 | 651 | 206 | 2 | no |
| 3 | M | 17 | 3 | 995 | 743 | 670 | 202 | 3 | no |
| 3 | M | 29 | 3 | 972 | 738 | 670 | 206 | 3 | no |
| 3 | M | 43 | 3 | 991 | 741 | 662 | 205 | 3 | no |
| 3 | L | 17 | 3 | 984 | 731 | 655 | 201 | 3 | no |
| 3 | L | 29 | 3 | 953 | 738 | 665 | 200 | 3 | no |
| 3 | L | 43 | 3 | 968 | 739 | 663 | 209 | 3 | no |
| 4 | M | 17 | 4 | 789 | 746 | 668 | 201 | 4 | no |
| 4 | M | 29 | 4 | 790 | 740 | 671 | 207 | 4 | no |
| 4 | M | 43 | 4 | 821 | 742 | 665 | 209 | 4 | no |
| 4 | L | 17 | 4 | 769 | 732 | 660 | 204 | 4 | no |
| 4 | L | 29 | 4 | 788 | 739 | 668 | 206 | 4 | no |
| 4 | L | 43 | 4 | 798 | 737 | 662 | 210 | 3 | no |
| 5 | M | 17 | 5 | 687 | 743 | 669 | 202 | 4 | no |
| 5 | M | 29 | 5 | 661 | 744 | 676 | 207 | 5 | no |
| 5 | M | 43 | 5 | 685 | 745 | 670 | 207 | 5 | no |
| 5 | L | 17 | 5 | 624 | 733 | 662 | 209 | 5 | no |
| 5 | L | 29 | 5 | 640 | 742 | 667 | 207 | 5 | no |
| 5 | L | 43 | 5 | 660 | 737 | 666 | 208 | 3 | no |
| 6 | M | 17 | 6 | 530 | 747 | 671 | 202 | 6 | no |
| 6 | M | 29 | 6 | 538 | 747 | 678 | 204 | 6 | no |
| 6 | M | 43 | 6 | 571 | 743 | 667 | 204 | 5 | no |
| 6 | L | 17 | 6 | 576 | 734 | 662 | 207 | 6 | no |
| 6 | L | 29 | 6 | 533 | 743 | 669 | 209 | 6 | no |
| 6 | L | 43 | 6 | 559 | 739 | 669 | 213 | 3 | no |
| 7 | M | 17 | 7 | 462 | 745 | 673 | 202 | 6 | no |
| 7 | M | 29 | 7 | 452 | 749 | 681 | 203 | 7 | no |
| 7 | M | 43 | 7 | 452 | 744 | 669 | 203 | 5 | no |
| 7 | L | 17 | 7 | 485 | 737 | 669 | 208 | 7 | no |
| 7 | L | 29 | 7 | 501 | 744 | 671 | 209 | 7 | no |
| 7 | L | 43 | 7 | 496 | 740 | 672 | 213 | 7 | no |
| 8 | M | 17 | 8 | 398 | 747 | 672 | 203 | 6 | no |
| 8 | M | 29 | 8 | 438 | 749 | 679 | 203 | 7 | no |
| 8 | M | 43 | 8 | 442 | 744 | 669 | 204 | 5 | no |
| 8 | L | 17 | 8 | 439 | 741 | 673 | 210 | 8 | no |
| 8 | L | 29 | 8 | 471 | 742 | 674 | 210 | 7 | no |
| 8 | L | 43 | 8 | 461 | 738 | 673 | 211 | 7 | no |
| 9 | M | 17 | 9 | 402 | 747 | 671 | 205 | 6 | no |
| 9 | M | 29 | 9 | 382 | 751 | 680 | 205 | 9 | no |
| 9 | M | 43 | 9 | 355 | 747 | 669 | 204 | 9 | no |
| 9 | L | 17 | 9 | 399 | 740 | 674 | 210 | 8 | no |
| 9 | L | 29 | 9 | 427 | 740 | 676 | 211 | 7 | no |
| 9 | L | 43 | 9 | 398 | 738 | 675 | 209 | 7 | no |
| 10 | M | 17 | 10 | 345 | 747 | 670 | 205 | 6 | no |
| 10 | M | 29 | 10 | 332 | 751 | 679 | 206 | 9 | no |
| 10 | M | 43 | 10 | 334 | 747 | 671 | 205 | 9 | no |
| 10 | L | 17 | 10 | 361 | 739 | 673 | 210 | 8 | no |
| 10 | L | 29 | 10 | 374 | 740 | 676 | 212 | 7 | no |
| 10 | L | 43 | 10 | 358 | 739 | 671 | 210 | 7 | no |
| 11 | M | 17 | 11 | 323 | 746 | 671 | 204 | 6 | yes |
| 11 | M | 29 | 11 | 344 | 748 | 677 | 209 | 9 | no |
| 11 | M | 43 | 11 | 333 | 749 | 673 | 206 | 11 | no |
| 11 | L | 17 | 11 | 371 | 741 | 675 | 210 | 8 | no |
| 11 | L | 29 | 11 | 356 | 739 | 677 | 214 | 7 | no |
| 11 | L | 43 | 11 | 335 | 739 | 671 | 209 | 7 | no |
| 12 | M | 29 | 12 | 292 | 750 | 678 | 209 | 9 | no |
| 12 | M | 43 | 12 | 296 | 749 | 673 | 206 | 11 | no |
| 12 | L | 17 | 12 | 339 | 741 | 674 | 210 | 8 | no |
| 12 | L | 29 | 12 | 341 | 738 | 676 | 214 | 7 | yes |
| 12 | L | 43 | 12 | 326 | 738 | 673 | 207 | 7 | yes |
| 13 | M | 29 | 13 | 270 | 751 | 677 | 209 | 9 | no |
| 13 | M | 43 | 13 | 274 | 749 | 675 | 207 | 11 | no |
| 13 | L | 17 | 13 | 311 | 742 | 674 | 209 | 13 | no |
| 14 | M | 29 | 14 | 266 | 752 | 679 | 210 | 14 | no |
| 14 | M | 43 | 14 | 254 | 750 | 675 | 210 | 14 | no |
| 14 | L | 17 | 14 | 322 | 742 | 673 | 208 | 13 | no |
| 15 | M | 29 | 15 | 256 | 753 | 681 | 210 | 15 | no |
| 15 | M | 43 | 15 | 271 | 748 | 675 | 212 | 14 | no |
| 15 | L | 17 | 15 | 298 | 742 | 675 | 207 | 13 | no |
| 16 | M | 29 | 16 | 242 | 751 | 679 | 211 | 15 | no |
| 16 | M | 43 | 16 | 225 | 749 | 676 | 213 | 14 | no |
| 16 | L | 17 | 16 | 283 | 742 | 675 | 207 | 13 | no |
| 17 | M | 29 | 17 | 230 | 748 | 678 | 211 | 15 | no |
| 17 | M | 43 | 17 | 256 | 751 | 676 | 214 | 17 | no |
| 17 | L | 17 | 17 | 287 | 742 | 676 | 207 | 13 | no |
| 18 | M | 29 | 18 | 210 | 747 | 678 | 211 | 15 | no |
| 18 | M | 43 | 18 | 204 | 751 | 677 | 215 | 17 | no |
| 18 | L | 17 | 18 | 273 | 743 | 677 | 206 | 18 | no |
| 19 | M | 29 | 19 | 218 | 748 | 678 | 211 | 15 | no |
| 19 | M | 43 | 19 | 234 | 751 | 677 | 216 | 17 | no |
| 19 | L | 17 | 19 | 275 | 744 | 678 | 209 | 19 | no |
| 20 | M | 29 | 20 | 226 | 747 | 680 | 209 | 15 | yes |
| 20 | M | 43 | 20 | 211 | 751 | 679 | 215 | 17 | no |
| 20 | L | 17 | 20 | 273 | 744 | 678 | 208 | 19 | no |
| 21 | M | 43 | 21 | 219 | 749 | 679 | 214 | 17 | no |
| 21 | L | 17 | 21 | 273 | 742 | 679 | 210 | 19 | no |
| 22 | M | 43 | 22 | 215 | 749 | 678 | 214 | 17 | yes |
| 22 | L | 17 | 22 | 256 | 741 | 678 | 211 | 19 | no |
| 23 | L | 17 | 23 | 272 | 739 | 676 | 211 | 19 | no |
| 24 | L | 17 | 24 | 250 | 740 | 676 | 210 | 19 | yes |


### v0.5.0 training and development selection complete

All six runs stopped by the registered patience rule: **101 arm-seed-epochs**, **202 distinct durable A/B checkpoint records**, **24 published round groups**. Epoch choices were locked before the new balanced development set was scored.

| Arm | Seed | Epochs run | Selected epoch | CALIB preferred /1120 | Correct selected | Wrong selected |
|:---:|---:|---:|---:|---:|---:|---:|
| M | 17 | 11 | 6 | 747 | 671 | 202 |
| M | 29 | 20 | 15 | 753 | 681 | 210 |
| M | 43 | 22 | 17 | 751 | 676 | 214 |
| L | 17 | 24 | 19 | 744 | 678 | 209 |
| L | 29 | 12 | 7 | 744 | 671 | 209 |
| L | 43 | 12 | 7 | 740 | 672 | 213 |

New balanced development results at threshold2.5 (128 sentences,1,302 non-punctuation words; canonical native-role/declared-feature metric):

| Arm | Seed | Preferred /1302 | Correct selected | Wrong selected | Abstained/missing |
|:---:|---:|---:|---:|---:|---:|
| v020 | 17 | 774 | 701 | 288 | 313 |
| v020 | 29 | 768 | 684 | 276 | 342 |
| v020 | 43 | 775 | 695 | 289 | 318 |
| J3 | 17 | 770 | 716 | 280 | 306 |
| J3 | 29 | 765 | 704 | 285 | 313 |
| J3 | 43 | 763 | 705 | 298 | 299 |
| M | 17 | 770 | 696 | 284 | 322 |
| M | 29 | 762 | 699 | 285 | 318 |
| M | 43 | 762 | 706 | 297 | 299 |
| L | 17 | 766 | 702 | 297 | 303 |
| L | 29 | 760 | 682 | 286 | 334 |
| L | 43 | 768 | 694 | 284 | 324 |

None of the 30 registered arm/threshold settings preserved every seed's preferred/correct counts and wrong-selection cap while improving the objective. All candidate arms had fewer preferred hits than the v0.2 reference in each seed; threshold changes cannot change this ranking. The preregistered fallback therefore retains **v0.2 at2.5** as comparison reference. This is not a new default-model promotion. Model/threshold choices were locked before the new check was opened. Final evaluation is in progress; its metrics and examples remain private. AB03 remains unopened.
