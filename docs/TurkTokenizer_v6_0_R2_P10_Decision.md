# TurkTokenizer v6.0 R2-P10 decision

R2-P10 tested one frozen-checkpoint change on CALIB: direct relations were activated from source probability alone instead of source probability multiplied by maximum head probability. Head choice, model parameters, CASE_GOVERNOR policy, and syntax outputs were unchanged.

## Result

| Variant | Macro F1 | Minimum-family F1 | OBJECT F1 | UAS | LAS |
|---|---:|---:|---:|---:|---:|
| A1 reference | 0.810756 | 0.717407 | 0.717407 | 0.878516 | 0.759907 |
| R2-P9 H21 parent | 0.802043 | 0.712068 | 0.712068 | 0.884311 | 0.765388 |
| R2-P10 | 0.801806 | 0.714084 | 0.714084 | 0.884311 | 0.765388 |

R2-P10 improved OBJECT by `+0.002016` over its H21 parent but remained `-0.003323` below A1. Macro F1 decreased by `-0.000236` versus H21 and stayed `-0.008950` below A1. The PARTICIPLE_HEAD preservation gate also failed.

The precommitted decision is `DROP_AFTER_SCREEN`. Source-only activation removed false positives but did not recover true positives, so further threshold or coupling tuning is not justified on this line.

Two independent executions produced byte-identical aggregate results. INTERNAL_VAL, TEST, and external holdouts remain unopened; no model parameters were trained or updated.
