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
| TRAIN fit | Complete: one deterministic TRAIN count fit |
| CALIB selection | Complete; alpha=0 fallback, locked before CHECK |
| Locked diagnostic evaluation | Complete; private M0/ZERO/fixed-alpha diagnostic artifacts retained |
| Promotion | NOT PROMOTED; CALIB selected zero, AB00 remains default |

Only aggregate TRAIN/CALIB results and status are published here. Models, raw examples, private diagnostic measurements and full evaluation artifacts remain outside the public repository.

The added factor cannot recover native-pruned relation plans. Inner sequence decoding remains exact within each retained configuration; the outer relation search remains approximate. This arm does not add discourse resolution or a complete dependency parser.

Sources: [Kiwi](https://github.com/bab2min/Kiwi#citation), [inspected SkipBigram implementation](https://github.com/bab2min/Kiwi/blob/f06a54db4748e4eb5b8ced127c281fc8fac73ea1/src/SkipBigramModel.hpp).

## TRAIN fit summary

The frozen 3,278-reference fit produced 2,548 eligible dependency events and 2,299 distinct lemma pairs. With minimum support 2, 175 pairs receive a score (170 positive, 5 negative). Unseen/low-support pairs remain neutral. Counts alone do not establish selection quality. CALIB ran after the fitted A/B artifact gate.

## CALIB selection

All preregistered alpha values (0, 0.25, 0.5, 1, 2) returned the same aggregate counts on the 1,520-word CALIB pool: 718 preferred analyses compatible with canonical role plus declared features, 575 correct committed choices, 409 incorrect committed choices, 536 abstentions/missing spans. Exact spans: 1,439; compatible candidate coverage: 1,080. These are not full-path accuracy measurements.

No nonzero setting met the required strict improvement, so alpha=0 is frozen. The zero adapter matched native M0 outputs exactly on all 128 CALIB sentences. The preregistered alpha=1 diagnostic was run, with no post-CHECK arm or threshold rescue.

## v0.1.0 closure — 2026-09-07

The bounded first AB03 experiment is complete and is not promoted. The selected alpha remains zero. All frozen inference/model/data identities and the separate stage gates were checked. The two 3,000-word regression pools and the locked diagnostic protocol were executed; detailed measurements stay private.

The initial evaluator stopped on a serialization-only equality assertion (integer dictionary keys in live output versus string keys in JSON-loaded output). Stored zero-control outputs agreed. The frozen original evaluator was preserved; a recorded measurement runner canonicalizes JSON only for that equality check and reuses hash-verified completed M0 outputs. The model, alpha lock, gold labels, scoring and metric definitions did not change.

CALIB evidence coverage was sparse: only 2 of 128 sentences had nonzero evidence in a retained configuration. Descriptive CALIB inspection identified nonfinite predicate/argument admission as a concrete follow-up question. This does not establish a general failure of distant context, nor does it justify combining AB02 automatically. A future isolated arm should distinguish a participle's external nominal/adjectival role from its internal verbal valency and test representation/plan changes separately from the learned distant score.

## v0.2.0 preregistration — internal nonfinite clauses

Preregistered starting status: implementation/contracts complete; new CALIB inference pending. The completed outcome is recorded below. This remains an isolated AB00-based AB03 experiment. No AB01/AB02 weights are imported. The verified v0.1.0 175-pair TRAIN model is reused byte-for-byte; there is no new fit, epoch loop, or random seed.

The repair retains a Part/Vnoun candidate's original NOUN/ADJ output, morphology features and analysis ID while opening an internal verbal frame. Possessor-marked predicates can take a compatible overt genitive subject; native verb frames supply object/oblique cases and voice behavior. A small inherent-agreement lookup for personal pronoun lemmas supplements missing candidate Person metadata without rewriting candidates. No relative/control subject is invented.

One internal clause is permitted per extra configuration. Its interior is removed from the outer argument scope; the clause head remains shared by the same analysis ID. Only that introduced clause receives clausal external labels. Prefix scope hypotheses are bounded and heuristic: maximum gap 12, maximum 8 hypotheses per block. All original M0 configurations survive, with at most 16 additional configurations (total maximum 33).

Controls: M0, disabled ZERO adapter, native equal-budget BUDGET (33 configurations), previous OLD1, repair-only R0, and repair+lexical R1. Alpha grid 0/0.25/0.5/1/2 is calibrated on new BOUN TRAIN sentences. Repair eligibility requires nonregressing preferred/correct/wrong counts and a strict improvement over M0. Positive alpha additionally must improve without regression over R0. Otherwise fall back to M0. Margin stays 2.5.

New CALIB has 128 sentences and 1,408 nonpunctuation words, balanced across bio/ess/news/pop. A separately partitioned CHECK remains unopened until the arm/alpha lock is durable. Prior AB02/AB03 pools, IMST TRAIN, original diagnostics and new synthetic probes are excluded by exact/near-duplicate checks. Document independence is not proved; official dev/test and sealed evaluation remain unopened.

Both 3,000-word pools and prior ambiguity/paired/relation diagnostics will run. A predeclared 40-case synthetic mechanism suite measures target-edge selection versus complete expected-edge availability in retained configurations. It is not human-adjudicated full-tree gold and is not used to select alpha.

| v0.2.0 stage | Status |
|---|---|
| Verified parent, code, technical contracts, data partition | Complete |
| Initial code/data/copied-model A/B gate | Complete; corrected R2 is canonical |
| New CALIB arm/alpha lock | Complete; repair-only R0 selected, alpha=0 |
| Locked diagnostic evaluation | Complete; preregistered acceptance gates passed; full artifacts retained privately |
| Promotion | R0 retained as an AB03 research reference; AB00 remains default; no automatic product promotion |

Primary annotation references: [Turkish ccomp](https://universaldependencies.org/tr/dep/ccomp.html), [acl](https://universaldependencies.org/tr/dep/acl.html), [VerbForm](https://universaldependencies.org/tr/feat/VerbForm.html). Public updates remain limited to protocol/status and aggregate TRAIN/CALIB information.

### Pre-CALIB technical revision R2

Before the first new CALIB inference, a combined-scope contract found that inserting an internal clause head could intercept a native automatic outer converb attachment. The graph adapter now orders only outer predicate plans for this connector; a parent role/link supplies the internal clause's external edge. Original R1 code/manifest and A/B start records are preserved. Corrected R2 contracts passed; R2 initial A/B is the canonical boundary before CALIB. No model, gold or measured CALIB result was changed.

### v0.2.0 CALIB lock

The selected setting is repair-only R0 (alpha=0), under the preregistered canonical-role/declared-feature objective. The reused lexical score did not add an eligible strict improvement over R0 at any positive alpha. Zero adapter outputs matched M0 on all 128 CALIB sentences.

| CALIB arm | Preferred, canonical+features | Preferred lemma+POS | Committed correct | Committed wrong | Abstained/missing |
|---|---:|---:|---:|---:|---:|
| M0 / ZERO / OLD1 | 659 | 807 | 530 | 369 | 509 |
| BUDGET | 656 | 802 | 526 | 357 | 525 |
| R0 and R with alpha 0.25/0.5/1/2 | 661 | 805 | 530 | 368 | 510 |

The canonical preference gain is small, and lemma+POS alone regresses by two. Equal-budget BUDGET has fewer wrong commitments but also fewer correct commitments; the repair does not dominate every metric. This is a locked candidate for further checking, not a promotion or proof of general improvement. CHECK evaluation starts only after the calibrated A/B gate.

## v0.2.0 closure — 2026-09-07

The locked diagnostic experiment is complete. The preregistered acceptance gates passed for the CALIB-selected repair-only R0 arm. The structural repair is retained as the next AB03 research reference. The reused lexical score supplied no eligible additional CALIB improvement and remains disabled. AB00 stays frozen and remains the default; this is not an automatic product promotion or proof of perfect/general language understanding.

All preregistered controls and regression pools were executed. The final read-only audit reconciles stored token-level records with aggregate results, verifies the unchanged frozen code/model/data and preserves the canonical pre-CALIB R2 and calibrated A/B records. Detailed CHECK measurements, examples and models remain private.

Remaining work separates admission of existing nonfinite candidates from ranking of already available joint plans. A bounded admission threshold can exclude plausible nonfinite readings; merely making a correct plan available does not ensure its selection. Individual regressions and scope/agreement limitations remain. Future changes require isolated controls and a new CALIB/held-out CHECK protocol; the CHECK opened in this experiment is now observed regression material.

## v0.3.0 preregistration — distant lexical evidence

This experiment isolates distant lexical improvements on frozen v0.2.0 repair-only R0. AB00 morphology, native n-gram, margin 2.5, structural repair and maximum 33 configurations remain fixed. No AB01/AB02 weights are imported.

Three isolated arms: E re-estimates the original direct-argument root PMI on expanded TRAIN; C conditions lexical evidence on role/case with empirical-Bayes backoff; D uses punctuation-bounded skip-root cooccurrence as soft candidate scores from roots on which all original analyses agree. D does not use previous predictions as anchors or infer referents. Its unaries can affect pruning; E/C score retained bound-role configurations. Inner decoding remains exact per retained configuration; outer search remains approximate.

Expanded FIT contains 3,278 IMST and 5,822 BOUN TRAIN sentences (92,105 nonpunctuation words). New CALIB contains 256 sentences (2,897 nonpunctuation words), 64 each bio/ess/news/pop. A separate CHECK remains unopened until the CALIB lock. Prior diagnostic pools and exact/near duplicates are excluded. Document independence is not proved; official dev/test remain unopened.

Weights 0.25/0.5/1/2/4/8 are selected on CALIB only. Eligibility requires strictly more preferred-correct analyses, committed-correct not lower and committed-wrong not higher than R0. Best isolated arms are retained as preregistered diagnostics even if ineligible. Only independently eligible E-or-C and D may be combined using their already selected weights; otherwise no combination is run.

The practical success criterion is at least +1 percentage point on both the fixed main word pool and the new CHECK, positive sentence-paired bootstrap 95% lower bound on CHECK, and the predeclared commitment/paired/ambiguity/mechanism/relation nonregression gates. This is an incremental research criterion, not sufficient final Turkish accuracy. Failure closes this bounded lexical line and moves planning to AB04, retaining useful structural findings separately.

| v0.3.0 stage | Status |
|---|---|
| Implementation, independent contracts, data split | Complete before fit |
| Initial A/B gate | Complete before TRAIN fit |
| TRAIN fit | Complete; one deterministic fit per estimator |
| CALIB selection | Complete; E alpha=8 locked; C/D fail independent eligibility |
| Locked diagnostic evaluation | Complete; practical improvement criterion failed |
| AB03/AB04 decision | Close this bounded AB03 lexical line; start independent AB04 |

Public updates remain limited to protocol/status and aggregate TRAIN/CALIB. Private CHECK and regression measurements, examples and models are retained in the experiment artifacts.

### v0.3.0 TRAIN fit

E produced 8,576 direct distant-argument events and 607 supported root pairs, versus 175 in the prior small model. C produced 16,667 direct role/case events including adjacent training arguments. D produced 161,726 skip-root events, 131,187 distinct pairs and 15,878 supported pairs across 11,177 roots. Larger support counts are coverage measurements, not evidence of better decisions. The fitted A/B gate precedes CALIB inference.

### v0.3.0 CALIB lock

The eligible setting is E with alpha=8. The native repair-only adapter matched the prior R0 on all 256 CALIB sentences. No combination is admitted because D fails independent nonregression. Each isolated estimator's best CALIB-ranked setting is retained as the preregistered diagnostic: E8, C8 and D8. These diagnostics cannot replace the selected arm after CHECK.

| CALIB setting | Preferred canonical+features | Committed correct | Committed wrong | Sentences with added evidence |
|---|---:|---:|---:|---:|
| R0 | 1386 | 1107 | 751 | 8 legacy relation-evidence sentences; coefficient zero |
| E8 | 1387 | 1108 | 749 | 27 relation-evidence sentences |
| C8 | 1386 | 1103 | 734 | 173 relation-evidence sentences |
| D8 | 1389 | 1120 | 757 | 119 anchor-evidence sentences |

The selected improvement is small. Broader evidence coverage does not establish useful discrimination. C8 trades away correct commitments; D8 increases wrong commitments. No parameter or threshold will be changed after the lock. Diagnostic evaluation follows the calibrated A/B gate.

## v0.3.0 closure — 2026-09-07

The selected E8 arm did not meet the preregistered practical improvement and nonregression gates. The locked diagnostic controls also supplied no basis for a CHECK-driven rescue. Expanded data, role/case conditional evidence and candidate-unanimous distant roots increased evidence reach, but this did not establish the required generalizing accuracy gain. The new lexical additions are not promoted.

The useful v0.2.0 structural repair remains archived separately. AB00 stays unchanged. This result closes the bounded lexical approaches tested here; it does not establish that all distant-context models are ineffective. Frozen sources, model/selection locks and stored row-level aggregates were reconciled. Private evaluation measurements and examples remain in the final A/B artifacts.

The next independent arm is [AB04 multilevel representation](TurkTokenizer_R5_AB04_Progress.md). It begins with lossless surface/candidate-path contracts and explicit component provenance, then requires a separately controlled coverage/selection experiment. A representation view alone is not an accuracy gain.
