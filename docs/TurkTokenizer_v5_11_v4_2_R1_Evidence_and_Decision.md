# TurkTokenizer v5.11-v4.2 R1 — Evidence and Decision

## Decision

v4.1 A3 is closed as `DROP_AFTER_SCREEN`; it is not a base for further tuning. The next controlled screen starts from the surviving A1 contextual-morphology posterior and changes only the direct-relation decision layer.

R1 replaces the independent `sigmoid(source) × softmax(head)` calibration for `OBJECT`, `POSS_HEAD`, and `PARTICIPLE_HEAD` with one length-normalized categorical decision over `NULL ∪ candidate heads`. `CASE_GOVERNOR`, morphology candidates, syntax heads, encoder size, sampling, optimizer, schedules, data splits, consensus targets, hard-negative protocol, and all quality gates remain unchanged.

## Why this is the next narrow experiment

A3 proved that top-20 lattice coverage is no longer the dominant ceiling: corrected joint lemma+morphology coverage is 0.9632 and relation-critical requirement coverage is 0.9574, yet the final screen reached only 0.8041 macro F1 and 0.7053 minimum-family F1.

The factorized A3 audit localizes the largest error:

| Diagnostic | OBJECT |
|---|---:|
| Source-token F1 | 0.6748 |
| Head top-1 given the gold source | 0.9334 |

The head selector is already strong when the source is known. The weak decision is whether a token instantiates the relation at all. A1 is the best existing base: its contextual morphology posterior raised OBJECT source F1 to 0.7288 and passed the controlled screen without any family regression.

The current direct decoder trains a source sigmoid and a conditional head softmax separately, then multiplies their probabilities. R1 instead makes `NULL` compete directly with every valid head in one normalized distribution. This is the smallest architecture change that targets the measured source-presence calibration error while retaining the successful biaffine head scorer.

## Primary-source support

- Turkish morphology and dependency structure are mutually informative, and joint lattice parsing can beat pipeline systems: Seeker & Çetinoğlu (2015), https://aclanthology.org/Q15-1026/.
- Morphology-aware representations improve parsing for agglutinative languages: Özateş et al. (2018), https://aclanthology.org/K18-2024/.
- Biaffine arc/label classifiers are an effective normalized graph-parsing decision layer: Dozat & Manning (2017), https://arxiv.org/abs/1611.01734 and https://aclanthology.org/K17-3002/.
- End-to-end semantic role models benefit from jointly deciding predicates/arguments and their relations instead of assuming a gold source: He et al. (2018), https://aclanthology.org/P18-1179/.
- Word-pair biaffine semantic-role classification is a strong syntax-agnostic formulation: Cai et al. (2018), https://aclanthology.org/C18-1233/.
- Turkish predicate-argument resources exist and make source/argument structure a linguistically grounded future auxiliary, but R1 does not add new data: TRopBank v2.0, https://aclanthology.org/2020.lrec-1.336/.

## Locked R1 formulation

For each direct family and source token `i`, let `z(i,j)` be the existing fused head logit for valid head `j`, and let `z_null(i)` be a new token-local null logit from A1 contextual relation and graph states. With `N_i` valid heads:

```text
joint_logits(i) = [z_null(i), z(i,1)-log(N_i), ..., z(i,N)-log(N_i)]
p(source_i) = 1 - p(NULL_i)
p(head_j | source_i) = softmax_j(z(i,j))
```

Absent sources target `NULL`. Positive or consensus-soft sources place their remaining mass on the existing conditional-head target. A balanced focal joint cross-entropy retains the locked positive share, gamma, uncertainty weights, and hard-negative head penalty.

The `-log(N_i)` term prevents longer sentences from receiving more non-null probability solely because they contain more candidate heads.

## Screen and stop rules

R1 is compared against A1, not against the weaker locked v4 or A3:

- survive if macro relation F1 gains at least 0.01 **or** minimum-family F1 gains at least 0.015;
- no family F1 regression;
- UAS and LAS may each regress by at most 0.005;
- absolute CALIB gates remain macro ≥0.90, min-family ≥0.87, UAS ≥0.88, LAS ≥0.80;
- `INTERNAL_VAL`, external holdouts, and official TEST splits remain sealed.

Only seed 51104 is permitted for the screen. Three-seed finalist evaluation is authorized only if the screen survives.

