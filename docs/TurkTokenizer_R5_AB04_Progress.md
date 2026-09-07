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
| Initial A/B gate | Being finalized before fit |
| Single deterministic TRAIN count fit | Pending |
| CALIB selection | Pending |
| Locked diagnostic evaluation | Pending |
| Acceptance and view attribution | Pending |

Public updates remain protocol/status and aggregate TRAIN/CALIB only. Private diagnostic metrics, raw examples and models remain in experiment artifacts.
