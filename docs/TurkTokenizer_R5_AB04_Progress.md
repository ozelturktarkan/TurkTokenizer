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
