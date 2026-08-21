# TurkTokenizer v5.11-v4.1 — Evidence Review and Controlled Ablation Precommit

## Decision

The running locked v4 experiment remains the baseline and is not modified. The evidence review found three material morphology bottlenecks that justify a separate v4.1 ablation line if v4 fails its CALIB gate:

1. The v4 morphology posterior is not context-sensitive: candidate attention is queried only from the static surface-word embedding before the sentence Transformer.
2. The frozen analyzer exposes ordered morpheme realizations and morphophonological changes, but the v4 lattice build discards those records and the model averages an unordered feature bag.
3. The top-20 analyzer lattice does not contain a compatible lemma+morphology candidate often enough for reranking alone to solve the task.

No CALIB labels were used in this investigation. `INTERNAL_VAL` and the external BOUN/IMST/Penn holdouts were not opened.

## Live v4 baseline snapshot

| Syntax epoch | Loss | UAS | LAS | UPOS |
|---:|---:|---:|---:|---:|
| 1 | 2.4480 | 0.7692 | 0.6321 | 0.8680 |
| 2 | 1.4753 | 0.8154 | 0.6734 | 0.8842 |
| 3 | 1.2160 | 0.8313 | 0.7048 | 0.8960 |
| 4 | 1.2675 | 0.8448 | 0.7126 | 0.8862 |

The combined syntax checkpoint score improved at epoch 4 despite a small UPOS dip. This is not a gate decision; relation training and CALIB selection have not finished.

## TRAIN-only morphology audit

The audit examined 178,652 TRAIN tokens and the frozen TRAIN+CALIB morphology lattice without reading CALIB rows.

| Diagnostic | Result |
|---|---:|
| Lattice fallback tokens | 4,194 (2.35%) |
| Tokens on surfaces with multiple TRAIN gold signatures | 43,253 (24.21%) |
| Lemma recall at top-20 | 89.64% |
| Mapped morphology recall at top-20 | 93.55% |
| Joint lemma+mapped morphology recall at top-20, all tokens | 85.68% |
| Joint recall at top-20, tokens carrying mapped morphology | 74.57% |

The audit uses only conservative UD-to-analyzer tag mappings and therefore is a candidate-space diagnostic, not a test accuracy. Even with that caveat, the result establishes two separate ceilings:

- A surface-only reranker cannot choose different pre-Transformer candidate distributions for homographs in different sentence contexts.
- A perfect reranker cannot select a correct path if the analyzer did not place one in the top-20 lattice.

The weakest candidate-recall areas include ability/potential, negation, progressive, some imperative/person paths, and lemma recovery through dative/ablative or morphophonological alternations. Numeric/apostrophe forms also trigger analyzer fallbacks because a harmony rule may receive a stem with no vowel.

## What the literature supports

The findings support a hybrid model, but not the simplistic claim that “morphological tokenization is always superior.” Turkish experiments show that BPE/WordPiece can still win downstream tasks, while a morphology-level tokenizer remains competitive and reacts differently to vocabulary allocation. This means morphology must earn its place through controlled downstream ablations rather than linguistic intuition alone ([Toraman et al., 2023](https://arxiv.org/abs/2204.08832)).

For morphologically rich languages, the strongest consistent architectural idea is to preserve ambiguity and resolve it jointly with context and syntax. The original Turkish/Hebrew lattice parser improved over pipeline systems, and later neural work showed that context-valid lattice representations and analyzer coverage materially affect parsing ([Seeker & Çetinoğlu, 2015](https://aclanthology.org/Q15-1026/), [Levi & Tsarfaty, 2024](https://arxiv.org/abs/2402.02564)). This directly motivates a context-conditioned candidate posterior in v4.1.

Turkish morphology is an ordered morphotactic process, not a set of independent flags. A syntactically expressive Turkish analyzer explicitly represents root irregularities, meta-morphemes, inflectional/derivational boundaries and surface alternations such as harmony, voicing, vowel deletion and buffer material ([Öztürel et al., 2019](https://aclanthology.org/W19-3110/)). The existing frozen v5.5.4 analyzer already carries much of this as ordered `realizations`; v4 currently throws it away. Retaining and encoding that sequence is therefore a low-risk information repair rather than a speculative new linguistic theory.

The Universal Dependencies project warns that Turkish treebanks still differ in tokenization, POS and feature conventions, including copulas, auxiliaries, multiple moods and syntactic-word boundaries ([UD Turkish overview](https://universaldependencies.org/tr/)). The current surface-group isolation, treebank-balanced sampling and consensus targets are therefore sound and should remain. A treebank/domain adapter may be tested later, but it must not replace annotation-consensus auditing.

Recent Turkish tokenization work gives two useful but still preprint-level ideas: canonical allomorph identifiers with a controlled open-vocabulary fallback, and a neural morphology-aware tokenizer that enforces exact encode/decode round trips ([Bayram et al., 2026](https://arxiv.org/abs/2508.14292), [Morpheus, 2026](https://arxiv.org/abs/2606.18717)). These are not adopted wholesale. The robust conclusion is narrower: keep surface fidelity independent of analysis normalization, explicitly measure reversibility, boundary alignment and fertility, and preserve raw/grapheme fallback paths.

For the wider Turkic family, vowel harmony and agglutination are shared tendencies but not identical algorithms. Cross-Turkic work explicitly localizes harmony and morphophonological realization to language-specific generation, and open HFST/Apertium transducers already exist for many languages ([Tantuğ et al., 2007](https://aclanthology.org/P07-2048/), [Tyers et al., 2019](https://aclanthology.org/W19-6010/)). The future cross-family architecture should therefore share the neural graph and universal feature interface while plugging in per-language analyzers, scripts and morphophonology. Turkish rules must not be copied unchanged into Kazakh, Kyrgyz, Tatar, Uyghur, Sakha or other branches.

## v4.1 architecture delta

### A. Contextual candidate posterior

Keep the current initial raw-surface, character and analyzer-prior representation. After the 8-layer encoder produces sentence-contextual states, rescore every token’s candidates using both the contextual state and the candidate representation. Add the analyzer score as an explicit learned monotonic prior. Feed the refined morphology to the morphology expert, graph expert and relation heads through a gated residual.

TRAIN-only optional supervision uses a partial-marginal loss over all candidates compatible with the gold lemma and conservatively mapped UD features. If no compatible candidate exists, the candidate loss is skipped. No gold candidate is injected during inference.

### B. Ordered realization encoder

Extend each frozen candidate with the analyzer’s existing ordered records:

```text
(morph tag, realized suffix surface, morphophonological changes, state)
```

Encode this sequence with a small shared sequence encoder. This preserves contrasts such as a single `POSS_3PL` realization versus `PLURAL → POSS_3SG`, as well as voicing, buffer consonants and zero person markers. The current unordered mean-feature embedding remains the ablation baseline.

### C. Candidate coverage repair

- Normalize `İ/i` after casefold as well as before it, including `i + U+0307`.
- Add a numeral/pronunciation-aware suffix adapter or conservative surface-suffix analysis so numeric apostrophe forms never call vowel-harmony logic with no vowel.
- Repair candidate generation for progressive, negative/potential, imperative, possessive chains and high-impact case/lemma alternations.
- Retain the raw/grapheme fallback even when morphology fails.

Before neural training, TRAIN-only joint lemma+mapped-morphology top-20 recall on morphology-bearing tokens must reach at least 95%; relation-critical case, possession and participle requirements must each reach at least 95% candidate recall.

### D. Lossless runtime contract

The current runtime preserves source spans, which is sufficient for this relation experiment, but a standalone generative tokenizer must also be exactly reversible without the original source buffer. The production contract therefore requires:

- raw code points/bytes as the decoding authority;
- grapheme-cluster features for learning;
- a separate normalized analysis channel;
- punctuation, whitespace and unknown symbols represented in the reversible stream;
- `decode(encode(text)) == text` on 100% of the locked fidelity suite.

### E. Turkic adapters

Turkish remains the first quality target. After it passes, the shared core should accept language-specific HFST/Apertium-compatible lattice providers, language/script embeddings and reversible transliteration views. Universal morphosyntactic tags and graph operations can be shared; harmony, morphotactics, lexical alternations and script mapping remain adapter-owned.

## Controlled ablation order

| ID | Variant | Purpose |
|---|---|---|
| A0 | Locked v4 | Unchanged baseline |
| A1 | Contextual posterior only | Measure contextual disambiguation with the old lattice |
| A2 | Ordered realizations only | Measure morphotactic/allomorphic sequence value without coverage changes |
| A3 | Candidate coverage repair only | Measure analyzer recall with the old model |
| A4 | Combined A1+A2+A3 | Test whether the gains compose |

Each screen uses the same locked TRAIN/CALIB protocol. A variant survives only if macro relation F1 improves by at least 0.01 or minimum-family F1 by at least 0.015, no family regresses, and neither UAS nor LAS regresses by more than 0.005. Finalists run seeds `51104`, `51105`, and `51106` and report mean, standard deviation, worst seed and paired surface-group bootstrap confidence intervals.

Absolute CALIB gates remain unchanged: macro relation F1 ≥ 0.90, minimum family F1 ≥ 0.87, UAS ≥ 0.88, LAS ≥ 0.80. `INTERNAL_VAL` opens once only after all four pass. BOUN, IMST and Penn remain sealed until the existing external Phase-5 protocol permits access.

## Activation rule

- If locked v4 is rejected before opening `INTERNAL_VAL`, activate A1–A4 while preserving the current split and seal.
- If locked v4 passes and consumes `INTERNAL_VAL`, do not reuse that validation set to choose v4.1. Treat v4.1 as a new generation and precommit a fresh validation resource before any promotion decision.

The machine-readable companion is `TurkTokenizer_v5_11_v4_1_Architecture_Delta_Precommit.json`; the reproducible TRAIN-only audit is `TurkTokenizer_v5_11_v4_1_MorphLattice_Audit.py` with its JSON result.
