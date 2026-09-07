# R5 AB00-R1 base candidate progress

Status: PRECOMMITTED — R1-F1 nonfinite feature propagation, v0.1.0.

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
- Four-arm wide regression pending.
- Detailed data, models, local hashes and per-example diagnostics remain in the private reproducible package.
