# R5 AB00-R1 base candidate progress

Status: COMPLETE — R1-F1 base candidate passes its observed paired guards; frozen-G8 integration retains regressions. No default promotion.

AB00-R1 is an isolated R5 base candidate. The original AB00 and AB04 G8 remain the references; this experiment does not change the independent v6/R4 training line.

## Problem and intervention

Some native verbal-noun and converb transitions discard previously established Polarity and Voice features. R1-F1 preserves these two features during those transitions and keeps suffix-contributed negation. Finite person, tense and mood are not copied wholesale into the nonfinite representation.

The suffix registry, lexicon, licensed surface paths, relation grammar, search budgets, n-gram model and decision margin stay fixed. Analysis IDs are recomputed from the repaired features. No reference analysis is injected at runtime.

## Fixed comparison

| Arm | Base | AB04 |
|---|---|---|
| AB00 | Original N0 | Off |
| R1 | N0 plus R1-F1 | Off |
| AB00_G8 | Original base | Frozen G8 |
| R1_G8 | R1-F1 base | Same G8 code, count model, weight 8 and tau 1 |

All four arms are specified before the wide regression run. There is no fit, threshold tuning, P8 merge or AB01/02/03 transfer. Repaired feature keys may change support from the frozen AB04 count model; this interaction is recorded without silently refitting or projecting back to incorrect features.

## Evaluation contract

Use the existing standalone and contextual regression suites, CALIB and observed context/protection diagnostics. Keep reference labels and annotation bridges fixed. Separate span alignment, missing lemma candidates, POS/representation mismatches and declared-feature mismatches; these categories are not adjudicated claims that the gold is wrong.

The original arms must reproduce their saved results. The candidate must preserve the same licensed surface paths, morpheme sequences, costs and raw-text reconstruction. Full feature compatibility, correct and wrong committed decisions, opposing-use pairs, labeled relations and sentence consistency are protected alongside lemma/POS preference.

Mechanism checks are assistant-authored implementation checks, not an independent benchmark. Existing development pools have been observed. No sealed or official dev/test set is opened, and no candidate is automatically promoted.

## State

- Source A/B package equality and frozen parent inputs verified.
- R1-F1 implemented; targeted feature and unchanged-path contracts passed.
- Four-arm wide regression completed; both original controls reproduced exactly.
- Detailed data, models, local hashes and per-example diagnostics remain in the private reproducible package.

## v0.1.0 result

| CALIB arm | Compatible candidate | Correct preference | Correct committed | Wrong committed | Correct heads | Exact labeled edges |
|---|---:|---:|---:|---:|---:|---:|
| AB00 | 2055 | 1421 | 1137 | 747 | 431 | 233 |
| R1 | 2072 | 1429 | 1144 | 739 | 431 | 233 |
| AB00_G8 | 2055 | 1744 | 1634 | 647 | 437 | 254 |
| R1_G8 | 2072 | 1753 | 1639 | 636 | 437 | 254 |

R1-F1 repairs actual feature loss while retaining the licensed surface/path inventory. The base-only candidate passed all 32 precommitted paired development guards. In the main contextual regression, lemma/POS preference did not change; declared-feature candidate coverage and committed decisions improved. This is primarily a representation repair, not evidence of general semantic disambiguation.

The frozen-G8 combination passed 30 of 32 paired guards. It improved compatible-candidate coverage and reduced wrong committed decisions in the observed CHECK and reserve diagnostics. However, some previously correct main-pool commitments became abstentions, and exact labeled-relation precision decreased. The original AB00 and G8 remain the defaults.

The component audit found a concrete representation/model interaction: newly retained Voice values change path keys. Some competing analyses lose an old negative prior because the frozen count model has insufficient support for the corrected key; correct preferences remain, but margins shrink. The experiment neither lowered the threshold nor refitted the model after observing these cases.

Final checks reconciled row counts, reproduced original controls, and verified lossless surfaces, candidate-bound graph endpoints, and the restricted feature changes. Mechanism contracts and observed regressions do not establish independent generalization.

## Next isolated work

Continue the base candidate with reviewed candidate-generation gaps and inflection-group representation. Missing lemma candidates must be separated from lemma-convention and alignment mismatches. After stabilizing the representation, rebuilding AB04 counts on authorized TRAIN only is a separate adaptation experiment; preserve this frozen-model comparison.

The reproducible private closure contains the source, frozen protocol, outputs, error-review ledgers and A/B packages. Sealed evaluation remains unopened.

## v0.2.0 coverage repair preregistration

Status: IMPLEMENTED — fixed comparison pending. No default promotion.

The next candidate extends R1-F1 with six explicit repairs: voiced imperative stems after zero TAM; possibility/ability scope after negation; restricted copular paths for questions, negative copula and postpositions; explicit abbreviation metadata and pronunciation-conditioned suffixes; a bound possessive root licensed by dictionary metadata; and one reviewed lexical vowel-drop attribute.

The four fixed arms are P1 (v0.1.0 N0), C2 (combined v0.2.0 N0), P1_G8 and C2_G8. G8 code, count model, weight 8, tau 1 and Q0 gate remain fixed. Both P1 controls must reproduce their saved v0.1.0 results. All six isolated repairs are additionally screened on CALIB with N0 only; this is diagnostic and does not authorize selecting a new combined candidate after retest.

Gold labels, primary matchers, corpus sizes and annotation bridges stay fixed. Surface/path coverage may change in this experiment and is audited explicitly. Correct preference, compatible-candidate coverage, correct/wrong committed decisions, relations, opposing-use pairs and sentence consistency remain distinct. Root/lexical-lemma convention conflicts are recorded without injecting aliases or changing labels to count them as new successes.

No training, threshold tuning, sealed evaluation or automatic promotion is part of this comparison. Local mechanism cases are implementation contracts, not independent linguistic adjudication. Full source, protocol and per-example evidence remain in the private reproducible package.
