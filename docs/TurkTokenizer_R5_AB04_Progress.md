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
| Initial A/B checkpoint | Prepared before CALIB |
| CALIB and safeguard selection | Pending |
| Locked regression and contextual retest | Pending |
| Repair acceptance | Pending |

Private metrics/examples and reproducibility artifacts remain with the experiment. Public updates contain protocol/status and aggregate CALIB only.
