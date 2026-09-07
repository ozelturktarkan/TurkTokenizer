# TurkTokenizer R5 — AB04 progress

## Independent start — 2026-09-07

AB03 v0.3.0 did not meet its preregistered practical lexical-improvement criterion. AB04 starts independently from frozen AB00/M0 v0.7.0 hybrid. AB03 repair/weights and AB01/AB02 learned additions are not automatically combined.

The initial v0.1.0 is a representation contract: preserve the whole raw word and gaps, expose each original morphological candidate path and sound-change trace, and reserve an explicit provenance field for independently verified components. The component inventory is initially empty. No spelling-only compound split or Morfessor discovery becomes a verified linguistic record automatically.

Raw text must reconstruct exactly, including whitespace, case and apostrophes. Dictionary lemma, normalized realization and raw character span are distinct. Trace arithmetic consistency does not prove linguistic correctness. Existing analysis IDs, candidate lists and native contextual decisions must remain unchanged.

The design is inspired by the multigranular surface/dictionary-form examples in [SudachiPy](https://github.com/WorksApplications/sudachi.rs/tree/develop/python); it does not transfer Japanese grammar or claim to reproduce Sudachi accuracy.

| Stage | Status |
|---|---|
| Independent AB00 source and implementation | Complete |
| Technical raw/path contracts | Passed |
| Initial A/B gate | Complete before full regression |
| Two 3,000-word regression controls | Complete; original morphology and native contextual outputs unchanged |
| Accuracy claim | None; initial view has no selection or coverage gain |

A subsequent isolated experiment must show which existing coverage/selection errors receive new usable information from independently verified whole-word/derivation features. That requires TRAIN/CALIB selection and a new CHECK. Simply exporting richer JSON does not count as a successful accuracy improvement. Private regression examples and measurements remain in experiment artifacts; this page publishes protocol/status only.

## v0.1.0 foundation closure

The raw-text/candidate-path representation checks and frozen regression protocol are complete. Candidate IDs and complete native decisions were preserved; realization-process consistency was checked without treating it as linguistic gold. The component inventory remains empty. This foundation is retained for the next independently preregistered coverage/selection experiment. It supplies no accuracy gain by itself. Source identities and verified A/B artifacts are retained privately.

## v0.2.0 preregistration — whole word and morphological path evidence

The next isolated AB04 experiment turns representation views into soft candidate evidence on frozen AB00/M0. No AB02/AB03 weights or AB03 structural repair are imported. Morphology, original analysis IDs, native n-gram, margin 2.5 and maximum 17 configurations remain fixed. The component inventory stays empty.

Controls: W uses whole-word lemma/output-POS counts; F uses only output-POS and native features; P uses root/output POS, ordered inflection/derivation groups and sound-change traces with structural backoff; J averages W and P. Set-valued compatible TRAIN targets distribute one vote over unique views, so duplicate analyses cannot multiply support. Path statistics compare compatible-target mass against uniform chance among offered views, with support thresholds, shrinkage and bounded scores. Per-token evidence is max-centered and enters before native plan pruning; it is not a calibrated probability.

Fit: 8,588 TRAIN sentences, 86,422 nonpunctuation words (3,278 IMST and 5,310 BOUN). New AB04-local CALIB has 256 sentences and 2,972 words, balanced across bio/ess/news/pop; a separate 256-sentence CHECK is withheld from AB04 fitting until the lock. These holdout sentences were previously in AB03 v0.3.0 statistical TRAIN. No AB03 parameters are imported, but this is not a globally unseen or sealed project test. Document independence is not proved; official dev/test remain unopened.

Weights 0.25/0.5/1/2/4/8 are selected on CALIB. Eligibility requires strictly better preferred-compatible count, committed-correct not lower and committed-wrong not higher than M0. The best CALIB setting for each view is also run as a predeclared diagnostic. No post-CHECK weight rescue.

Practical acceptance requires at least +1 percentage point on main/CHECK preferred accuracy, positive sentence-paired bootstrap 95% lower bound on CHECK and the commitment/paired/relation/ambiguity/retention guards. Additional multilevel value is tested separately: J must beat separately calibrated W and F with predeclared minimum increments, positive paired intervals and protected controls. A whole-word-only gain is not automatically a path-representation gain.

| v0.2.0 stage | Status |
|---|---|
| Implementation, independent contracts, partition | Complete before fit |
| Initial A/B gate | Complete before fit |
| Single deterministic TRAIN count fit | Complete; model frozen before CALIB |
| CALIB selection | Complete; J with weight 8 locked before CHECK |
| Locked diagnostic evaluation | Complete; all five preregistered arms evaluated |
| Acceptance and view attribution | Not accepted; protected controls failed; no promotion |

Public updates remain protocol/status and aggregate TRAIN/CALIB only. Private diagnostic metrics, raw examples and models remain in experiment artifacts.

### v0.2.0 TRAIN fit

The deterministic count fit processed 86,422 nonpunctuation words. It used 62,919 aligned words with at least one original candidate compatible with canonical role and declared features; 17,263 had no compatible candidate and 6,240 lacked an exact span. These exclusions are supervision limits, not solved errors.

The model contains 21,074 whole-word types. Flat/coarse/fine patterns total 1,507/4,290/8,259; with the minimum five-opportunity gate, supported patterns are 736/1,437/1,900. Counts alone do not establish accuracy. The fitted A/B record precedes CALIB inference.


### v0.2.0 CALIB lock

The 24 positive settings and exact zero control are complete. J at weight 8 is the locked eligible selection. Each view's highest-ranked CALIB setting is also weight 8; these four settings remain predeclared diagnostics, not alternatives to be selected after CHECK.

| CALIB arm | Compatible preferred | Committed correct | Committed wrong |
|---|---:|---:|---:|
| M0 | 1,421 | 1,137 | 747 |
| W8: whole word | 1,716 | 1,619 | 724 |
| F8: flat features | 1,711 | 1,539 | 677 |
| P8: morphological path | 1,739 | 1,610 | 678 |
| J8: word and path | 1,870 | 1,779 | 622 |

All counts use the same 2,972-word CALIB denominator; candidate coverage is unchanged. These are selection measurements, not final accuracy evidence. The adapter's zero setting exactly matched native output for all 256 CALIB sentences. No weight search is extended after this lock.


### v0.2.0 closure

Frozen diagnostic evaluation and row-level reconciliation are complete. Original morphology and native candidate objects remain unchanged. The selected J8 setting fails the preregistered protected contextual-pair and relation guards; the separate multilevel-attribution criterion is also not met. No diagnostic arm is substituted for the locked selection, and no automatic promotion occurs.

The private evaluation distinguishes aggregate selection gains from damage to contextual readings, commitment behavior and partial-graph coverage. A possible subsequent experiment would address conflict between learned priors and sentence relations, with contextual safeguards declared before selection. No such repair or post-CHECK retuning is part of v0.2.0.

This CHECK is now observed development material. Its earlier AB03 TRAIN exposure remains disclosed above; it must not be reused as a globally unseen final test. Detailed private results, examples, model and reproducibility records are retained with the experiment.


## v0.3.0 preregistration — pruning and contextual-prior conflict

This is an isolated repair on the identical v0.2.0 whole-word/path count model. No additional model fit, AB02/AB03 parameter transfer, morphology change or new compound inventory is introduced.

Two changes are separated. Q ranks partial plans using bound unary scores relative to each token's best unary, equivalent to completing all unbound tokens with their best unary and dropping one common sentence constant. This removes a score-origin dependence from native partial-plan pruning; it does not make the bounded search exact.

G obtains a Q0 reference sentence solution. If the strongest whole-word/path prior groups disagree with the reference preferred lemma/POS, the prior is scaled by tau/(tau+d), where d is the reference max-marginal gap against the prior-best groups. Every finite gap retains positive evidence. The final sentence is jointly decoded again; reference choices and relations are not hard-bound or spliced into the result.

Controls are native AB00 (N0), exact old J8 (N8), pruning-only Q0, uniform repaired-pruning J weights (U), and contextual gating (G). U weights and G tau values are 0.5/1/2/4/8; G has maximum prior weight 8. The uniform controls test whether simply weakening priors explains the effect.

CALIB selection now requires the predeclared observed paired/relation/ambiguity/retention safeguards as well as aggregate preferred and committed-decision criteria. The main 22 pairs remain outside this setting selection. The repair cannot be rescued by switching to a diagnostic arm after retest.

All CALIB, protected examples, main regression, CHECK and reserve pools are already observed project development material. The old count model still excludes its CALIB/CHECK, whose prior AB03 TRAIN exposure remains disclosed. This is a controlled repair/retest, not a new unseen final evaluation. Official dev/test remain unopened.

| v0.3.0 stage | Status |
|---|---|
| Parent source/model verification | Complete; identical count model |
| Arithmetic and native-output contracts | Passed |
| Initial A/B checkpoint | Complete before CALIB |
| CALIB and safeguard selection | Complete; G1 locked before retest |
| Locked regression and contextual retest | Complete; original native and J8 outputs reproduced |
| Repair acceptance | G1 not accepted; reserve-decision and correct-head guards remain unmet |

Private metrics/examples and reproducibility artifacts remain with the experiment. Public updates contain protocol/status and aggregate CALIB only.


### v0.3.0 CALIB lock

G1 (maximum J weight 8, tau 1) is the eligible locked selection. U0.5 is the eligible uniform-weight comparison. N0/N8/Q0 remain the preregistered controls. Higher-count settings that fail protected development guards are ineligible.

| CALIB setting | Compatible preferred | Committed correct | Committed wrong |
|---|---:|---:|---:|
| N0 | 1,421 | 1,137 | 747 |
| N8 | 1,870 | 1,779 | 622 |
| Q0 | 1,417 | 1,148 | 756 |
| U0.5 | 1,621 | 1,292 | 638 |
| G1 | 1,744 | 1,634 | 647 |

The denominator is 2,972 words throughout. These are observed development-selection measurements, not independent final results. The model and settings are fixed for the next retest.


### v0.3.0 closure

The locked G1 repair improves the previously damaged contextual-pair and protected-relation behavior and passes those guards. Full acceptance is still not met: the reserve wrong-commitment and correct-head-count guards fail. The selected setting and count model remain unchanged; no automatic promotion occurs.

The uniform U0.5 diagnostic meets the predeclared retest criteria, but it is not substituted for G1 after viewing results. It is retained as a separate research candidate. The pruning-only control fixes score-origin dependence without establishing a broad accuracy gain; its interaction with the gate is not fully isolated by this experiment.

Post-lock inspection separates newly committed reserve errors, legacy annotation/representation differences, and partial-graph coverage losses. No gold relabeling or inference retuning was performed to remove failed gates. Further work should validate annotation mappings and address phrase/possessive relation coverage before another weight search.

Frozen-file identities, original native/J8 reproduction, row-level metric reconciliation, private evaluation and reproducibility artifacts are complete. All outcomes remain observed development evidence rather than unseen final-test claims.


## v0.4.0 preregistration — matched upper weights and graph safeguards

The frozen v0.3.0 parent and unchanged v0.2.0 count model have been verified. There is no additional fit or morphology change. Initial contracts and two durable initial artifacts are complete before CALIB.

A 2x2 comparison at maximum weights 0.5/2/4/8 separates native versus Q final-plan pruning and uniform versus gated prior evidence. Tau stays fixed at 1. The gate reference is always Q0, including native-final-pruning arms; changing the reference pass itself is not part of this contrast. N0/N8/Q0 remain reproduction controls. There are 19 declared runs including controls; no extension after retest.

CALIB eligibility retains the previous commitment and protected contextual guards and adds nonregression in correct heads, coarse labeled edges, exact labeled edges and exact labeled precision. The old selection rule is also recorded as a diagnostic. A single eligible setting is locked before retest; fixed old controls and the four factorial cells at its upper weight are the declared comparisons. Passing diagnostic settings cannot replace a failed locked choice afterward.

The legacy morphological evaluator and all reference labels stay unchanged. A decision-blind review queue records schema/feature disagreements without declaring them annotation errors; independent adjudication is pending. The legacy graph metric compares relation bases, so exact subtype equality is now reported and guarded separately. Sentence-level all-compatible counts are supplementary, not claims of complete semantic correctness.

All pools remain observed project development material with the prior AB03 exposure described above. No official dev/test or unseen final evaluation is opened. Publication remains protocol/status and aggregate CALIB only.


### v0.4.0 CALIB lock

All 19 preregistered runs are complete. Q-G8 (maximum weight 8, tau 1, Q final pruning) is selected again; it is inference-equivalent to v0.3.0 G1. The additional graph eligibility checks do not change the selected setting. Lower-weight arms provide different tradeoffs but do not win the declared ranking. This is not an improved-model claim.

| CALIB arm | Compatible preferred | Committed correct | Committed wrong | Correct heads | Exact labeled edges | Eligible |
|---|---:|---:|---:|---:|---:|---|
| N-G0.5 | 1587 | 1275 | 659 | 459 | 257 | No |
| N-G2 | 1648 | 1417 | 655 | 489 | 272 | Yes |
| N-G4 | 1694 | 1541 | 657 | 468 | 264 | Yes |
| N-G8 | 1740 | 1630 | 653 | 437 | 255 | Yes |
| N-U0.5 | 1616 | 1277 | 631 | 471 | 268 | Yes |
| N-U2 | 1726 | 1470 | 581 | 472 | 269 | No |
| N-U4 | 1816 | 1648 | 581 | 414 | 240 | No |
| N-U8 | 1870 | 1779 | 622 | 370 | 219 | No |
| N0 | 1421 | 1137 | 747 | 431 | 233 | No |
| N8 | 1870 | 1779 | 622 | 370 | 219 | No |
| Q-G0.5 | 1582 | 1281 | 663 | 473 | 264 | No |
| Q-G2 | 1649 | 1428 | 648 | 488 | 272 | Yes |
| Q-G4 | 1695 | 1544 | 652 | 472 | 270 | Yes |
| Q-G8 | 1744 | 1634 | 647 | 437 | 254 | Yes |
| Q-U0.5 | 1621 | 1292 | 638 | 479 | 275 | Yes |
| Q-U2 | 1732 | 1470 | 578 | 464 | 267 | No |
| Q-U4 | 1823 | 1657 | 575 | 415 | 243 | No |
| Q-U8 | 1873 | 1782 | 619 | 373 | 220 | No |
| Q0 | 1417 | 1148 | 756 | 447 | 243 | No |

Morphological counts share a denominator of 2,972 words. Graph counts describe an aligned partial graph, not full UAS/LAS. Exact labels include subtypes; old coarse-label metrics remain recorded separately. All these data are observed selection material.

The fixed diagnostics are N0/N8/Q0, Q-U0.5, and the four native/Q by uniform/gated cells at weight 8. The setting and model are locked in dual durable artifacts before retest. There is no retest-based substitution or new weight extension.


### v0.4.0 closure

The eight locked retest diagnostics and row-level reconciliation are complete. Q-G8 exactly reproduces v0.3.0 G1 on the original morphology, contextual, commitment and graph measurements. It still fails the reserve wrong-commitment and correct-head guards; adding exact-label safeguards does not turn it into an accepted repair. There is no automatic promotion or post-retest setting substitution.

At matched maximum weight, native versus Q final pruning has only a small observed difference and does not remove the remaining failure pattern. This contrast holds the Q0 gate reference fixed; it does not test changing that reference.

Decision-preserving replay localizes most lost direct heads to final joint ranking, with another group lost in outer configuration pruning. Exact previously correct relations are distinguished from correct-head/wrong-label cases. Some lost paths involve different analyses within the same lemma/POS group; identical output features can also coexist with different lexeme/root identities. These are diagnostic associations, not evidence that all such analyses can safely be merged or that Q0 decisions should be copied.

The next repair should investigate relation-compatible morphological paths within shared sentence scoring and the stage at which valid alternatives disappear. Broader weight sweeps or blanket possessive bonuses are not established solutions. The decision-blind annotation review queue remains unadjudicated; no reference relabeling occurred. Full-sentence compatibility is reported separately from word accuracy and does not establish semantic correctness.

Frozen identities, unchanged candidates/spans, fixed-reference factorial evidence and legacy-result reproduction passed their checks. Public details remain protocol/status and aggregate CALIB; private retest tables, examples and the reusable v0.4.0 evaluation stay in the experiment artifacts.


## v0.5.0 preregistration — shared evidence in relation-plan proposals

The v0.4.0 final A/B artifacts and all 274 manifested files were restored and verified. This repair keeps the same morphology, count model, native relation licenses, numerical structural scores and final sentence objective. There is no new fit or AB02/AB03 transfer.

The diagnosed mismatch is in bounded proposal search: modifier combinations, role beams and local plan inventories can discard analysis-bound variants before seeing the unary evidence used in the final decoder. I8 changes the 12-plan inventory ranking to relation_weight * raw_plan_score plus bound unaries relative to each token's best unary. P8 applies the same priority earlier, to modifier combinations, role beams and best-support ranking. The native grammatical tests and raw plan scores are unchanged; unaries are not added to them and remain counted once in the final shared objective. Ngram remains absent from approximate proposal priority.

Six fixed arms: N0, Q0, parent G8, I8, P8, and P0 (full proposal repair without the AB04 prior). Weight 8 and tau 1 remain fixed. The Q0 gate reference is unchanged for I8/P8. Search budgets stay at modifier limit 4, modifier-combination limit 32, role beam 24, local inventory 12 and up to 17 final configurations.

CALIB selection is restricted to I8/P8 that pass the existing AB00 commitment/contextual/graph safeguards and also preserve parent G8 preferred count, wrong commitment, correct heads and exact labeled edges, with a strict preferred or exact-label gain. The declared preferred/correct/wrong tie-break ranking stays fixed. Fallback is G8 with no new repair selected. All six arms are predeclared retest diagnostics; none can replace the locked choice afterward.

The 21 AB00 acceptance checks remain reported. Repair evidence is assessed separately against G8 for main/CHECK preferred counts, main/CHECK/reserve wrong commitments, contextual pairs/relations, and correct heads/exact labeled edges, requiring a strict relation gain. No automatic promotion follows an observed-set pass.

Independent contracts recover a supported morphological path that a native one-state role beam discards, while retaining its raw structural score. Score-origin invariance, candidate-order invariance, grammatical case licensing, fixed gate evidence, raw candidate preservation and independent reconstruction of the once-counted final objective passed. Initial dual durable artifacts precede CALIB.

All evaluation pools remain previously observed development material. No gold relabeling, unseen final test or official dev/test opening occurs. Publication remains protocol/status and aggregate CALIB only.
