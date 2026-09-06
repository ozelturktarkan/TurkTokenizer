# TurkTokenizer R5 — AB03 progress

## Independent arm

AB03 v0.1.0 starts from frozen AB00/M0 (v0.7.0 hybrid). AB01 changes and AB02 learned weights are absent. It is separate from the v6/R4 line in the repository README.

This narrow first arm adds TRAIN-estimated nonadjacent predicate–argument lemma association to existing scope-compatible relation configurations. It is inspired by Kiwi's use of distant cooccurrence; it is not a reproduction of Kiwi or its reported accuracy.

## Frozen protocol

- Fit once on the same 3,278 IMST TRAIN references; no neural training, epochs, or stochastic seeds.
- Count annotated nsubj/obj/iobj/obl pairs with distance 2–12 token indices. Pool relation/case for the lexical pair; keep native valency and clause constraints.
- Minimum pair count 2. Score: n/(n+5) × clip(log(nN/(n_head n_dep)), −2, 2). Unseen pairs contribute zero.
- Mean evidence over eligible, explicitly bound roles in a retained configuration. Add only after native pruning; morphology, native n-gram, search budgets and margin threshold 2.5 stay fixed.
- CALIB: 128 new BOUN TRAIN sentences, 32 each from bio/ess/news/pop (1,520 nonpunctuation words). Exclude earlier diagnostic pools and exact/near duplicates with IMST TRAIN.
- Alpha grid: 0, 0.25, 0.5, 1, 2. Nonzero eligibility requires CALIB preferred/correct not lower and wrong not higher than M0, plus a strict improvement. Otherwise select zero. Fixed alpha=1 is a preregistered diagnostic, not a post-CHECK rescue.
- Freeze alpha before opening a separately partitioned CHECK. Preserve both 3,000-word regression pools and paired/ambiguity/relation diagnostics.
- Initial, fitted, calibrated and final artifacts use separate verified A/B stage records.

## Stage log

| Stage | Status |
|---|---|
| AB00 core and source identities | Verified |
| Data partition and preregistration | Complete before fit |
| Independent contracts | Passed: native contracts, count arithmetic, 24 exhaustive configuration/path combinations and all max-marginals, bound endpoints, scope guard, candidate-order decision invariance |
| TRAIN fit | Pending |
| CALIB selection | Pending |
| Locked diagnostic evaluation | Pending |
| Promotion | No automatic promotion; AB00 remains default |

Only aggregate TRAIN/CALIB results and status are published here. Models, raw examples, private diagnostic measurements and full evaluation artifacts remain outside the public repository.

The added factor cannot recover native-pruned relation plans. Inner sequence decoding remains exact within each retained configuration; the outer relation search remains approximate. This arm does not add discourse resolution or a complete dependency parser.

Sources: [Kiwi](https://github.com/bab2min/Kiwi#citation), [inspected SkipBigram implementation](https://github.com/bab2min/Kiwi/blob/f06a54db4748e4eb5b8ced127c281fc8fac73ea1/src/SkipBigramModel.hpp).
