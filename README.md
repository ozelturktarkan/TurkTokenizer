# TurkTokenizer

TurkTokenizer is an open research project for lossless Turkish tokenization, morphology-aware candidate generation, and morphosyntactic relation graphs. The current v5.11 line combines raw surface tokens, a Unicode character encoder, a frozen top-20 morphology lattice, an eight-layer relative-position Transformer, dependency structure, and specialized relation experts.

This repository is a research snapshot, not a production release. Reported scores are CALIB-only architecture-selection results. The sealed `INTERNAL_VAL`, external BOUN/IMST/Penn holdouts, official TEST splits, corpus files, derived `.pkl` packages, and model checkpoints are not included.

## Current state

| Line | Decision | Macro F1 | Minimum-family F1 | UAS | LAS |
|---|---:|---:|---:|---:|---:|
| v3S BiLSTM | Rejected before `INTERNAL_VAL` | 0.7606 | 0.6291 | — | — |
| v4 locked baseline | Rejected before `INTERNAL_VAL` | 0.7972 | 0.7025 | 0.8752 | 0.7552 |
| v4.1 A1 contextual posterior | Keep for finalist screening; absolute gates failed | 0.8108 | 0.7174 | 0.8785 | 0.7599 |
| v4.1 A2 ordered realizations | Drop after screen | 0.8061 | 0.6918 | 0.8769 | 0.7602 |
| v4.1 A3 coverage repair | Drop after screen | 0.8041 | 0.7053 | 0.8778 | 0.7569 |
| v6.0 R2-P9 repair | Drop after screen | 0.8020 | 0.7121 | 0.8843 | 0.7654 |
| v6.0 R2-P10 decoupled decision | Drop after screen | 0.8018 | 0.7141 | 0.8843 | 0.7654 |
| v6.0 R3-P1 R1 null-arc decision | Drop after screen | 0.8051 | 0.7118 | 0.8831 | 0.7643 |
| v6.0 R3-P2 paired ranking-loss ablation | Drop after screen | 0.8141 | 0.7247 | 0.8868 | 0.7678 |
| v6.0 R3-P3 family-isolated ranking transfer | Drop after screen; R3 closed | 0.7795 | 0.7139 | 0.8831 | 0.7643 |

The v6.0 R2-P9 repair line restored the selected Syntax E20 boundary with a repaired morphology lattice, conflict-aware source supervision, a Syntax E70 ceiling, Relation/Hard-Negative E50 ceilings, and patience 9 for all three stages. Syntax closed at E42 with E38 selected, Relation closed at E37 with E28 selected, and Hard-Negative closed at H21 with H12 selected. The final TRAIN/CALIB screen yielded macro F1 `0.8020`, minimum-family F1 `0.7121`, `UAS=0.8843`, and `LAS=0.7654`; the precommitted decision is `DROP_AFTER_SCREEN`. Sealed evaluation remains unopened. See [the R2-P9 decision note](docs/TurkTokenizer_v6_0_R2_P9_Decision.md).

A CALIB-only A1–R1–H21 error decomposition found that H21 improves OBJECT source discrimination and head ranking separately, but the product-coupled direct-edge score does not retain those gains. R2-P10 froze the model and changed only the direct-relation activation score. It improved OBJECT F1 by `+0.0020` over H21 but remained below A1 and slightly reduced macro F1, so the precommitted decision is `DROP_AFTER_SCREEN`. See [the R2-P10 decision](docs/TurkTokenizer_v6_0_R2_P10_Decision.md).

R3-P1 returned to the frozen R1 null-arc checkpoint and changed only the direct-relation activation score. Source-only activation reduced OBJECT and macro F1 versus R1, so every promotion gate except the unchanged CASE_GOVERNOR policy failed. The precommitted decision is `DROP_AFTER_SCREEN`; post-hoc decision rescue is closed. See [the R3-P1 decision](docs/TurkTokenizer_v6_0_R3_P1_Decision.md).

R3-P2 is closed as a paired TRAIN/CALIB loss ablation. The ranking-loss
candidate yielded macro F1 `0.8141`, minimum-family F1 `0.7247`,
`UAS=0.8868`, and `LAS=0.7678`. It passed 10 of 12 precommitted gates, but
missed the absolute `CASE_GOVERNOR` and `PARTICIPLE_HEAD` regression limits,
so the precommitted decision is `DROP_AFTER_SCREEN`. Both arms, two independent
paired-decision executions, and their persistent A/B packages are verified.
Detailed per-family diagnostics and private integrity hashes remain in the
private closure packages; sealed evaluation remains unopened. See
[the R3-P2 precommit](docs/TurkTokenizer_v6_0_R3_P2_Precommit.md),
[the R3-P2 decision](docs/TurkTokenizer_v6_0_R3_P2_Decision.md), and
[candidate progress](docs/TurkTokenizer_v6_0_R3_P2_Candidate_Progress.md).

R3-P3 is closed as `DROP_AFTER_SCREEN`, and the R3 line is complete. Its original masked-training design was invalidated after Relation E01 because the Syntax E10 start boundary could not represent the completed R1 protected branches; E02 did not run and the diagnostic E01 values were never treated as a result. The corrected v2 experiment grafted exactly 123 direct-family tensors (2,222,643 parameters) from R3-P2 onto the completed frozen R1 checkpoint with zero optimizer steps. It preserved R1 `CASE_GOVERNOR`, UAS, and LAS exactly, but yielded macro F1 `0.7795`, minimum-family/OBJECT F1 `0.7139`, `UAS=0.8831`, and `LAS=0.7643`, passing only those three protected-metric gates out of twelve. POSS_HEAD and PARTICIPLE_HEAD also fell sharply, so the R3-P2 ranking gain is representation- and calibration-entangled rather than localized in the donor scorer modules. Final A/B closure packages, including the audit checkpoint, were re-materialized and checksum-verified. See [the corrected v2 precommit](docs/TurkTokenizer_v6_0_R3_P3_v2_Precommit.md), [the decision](docs/TurkTokenizer_v6_0_R3_P3_Decision.md), and [the draft R4 plan](docs/TurkTokenizer_v6_1_R4_Plan.md).

A3 was restarted cleanly under its fixed-seed, interruption-safe precommit and completed all syntax, relation, hard-negative, calibration, audit, and screen stages. The final CALIB screen yielded macro F1 `0.8041`, minimum-family F1 `0.7053` (`OBJECT`), `UAS=0.8778`, and `LAS=0.7569`. Its macro and minimum-family gains over the locked v4 baseline were below the precommitted survival thresholds, and `CASE_GOVERNOR` regressed by `-0.0078`; the decision is `DROP_AFTER_SCREEN`. The factorized audit identified source-token detection, rather than top-20 morphology coverage or conditional head attachment, as the dominant remaining OBJECT bottleneck. `INTERNAL_VAL` and sealed evaluation remain unopened.

The authoritative current state is [STATUS.md](STATUS.md) and [TurkTokenizer_v6_0_Quality_Ledger_v5.json](project_state/TurkTokenizer_v6_0_Quality_Ledger_v5.json).

## Scientific contract

- Preserve raw surface text for lossless decoding; normalization is an analysis view, not a rewrite of user input.
- Model Turkish-specific casing, apostrophes, vowel harmony, consonant alternations, derivation, inflection, and productive agglutination as testable candidate-generation rules.
- Keep the neural architecture and data split locked while evaluating one ablation at a time.
- Use only TRAIN for gradients and TRAIN-only candidate-space diagnostics.
- Use CALIB for checkpoint, threshold, and architecture screening.
- Never open `INTERNAL_VAL` unless every precommitted CALIB gate passes.
- Keep BOUN, IMST, Penn, and official TEST splits sealed until the Phase-5 protocol permits access.
- Reject gold-candidate injection, oracle features, label leakage, and post-hoc threshold rescue.

The long-term target is at least 95% on fresh, precommitted, multi-domain Phase-5 evaluation. No intermediate result is promoted merely because training completed.

## Repository layout

- `src/`: frozen analyzer, runtime tokenizer, and a hash-free public corpus verifier.
- `contracts/`: hash-free public architecture summary and corpus-provenance template.
- `audits/`: public-safe aggregate summaries without sealed-resource metadata.
- `docs/`: decision reports and completed A1/A2 training logs.
- `project_state/`: current machine-readable ledger.
- `data/`: acquisition and seal policy; no datasets are redistributed here.

Detailed split inventories, local corpus hashes, checkpoint hashes, sealed-resource metadata, serialized lattices, and model weights remain outside the public repository. Their authoritative copies are retained in the project Library. See [PUBLICATION_POLICY.md](PUBLICATION_POLICY.md).

## Reproduction outline

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Acquire the listed upstream corpus files from `contracts/Public_Corpus_Provenance_Template.json`. Copy that template to a local manifest and fill its `blob_sha` placeholders from the authorized locked manifest before verification; exact local lock values are intentionally not published.

```bash
python src/TurkTokenizer_public_verify_corpora.py \
  --directory data/corpora_exact \
  --manifest path/to/local_locked_manifest.json \
  --roles V4_TRAINING_POOL \
  --output data/public_verification_result.json
```

The locked data builder, neural training drivers, detailed precommits, and checkpoint-resume state are retained in the project Library. They will be published only after being refactored into a hash-free release interface that cannot disclose local or sealed-resource metadata. The public repository already exposes the tokenization/analyzer core, architecture summary, aggregate results, and falsifiable quality policy.

## License and data

Code and repository-authored documentation are licensed under Apache-2.0. Third-party corpora retain their own licenses and are not covered by this repository's license. See [data/README.md](data/README.md).

## Türkçe özet

Bu depo; Türkçenin sondan eklemeli yapısını, ek-kök ilişkilerini, ünlü uyumlarını, ses olaylarını ve sözdizimsel ilişkilerini kayıpsız yüzey tokenlarıyla birlikte modellemeyi hedefleyen açık araştırma projesidir. Henüz nihai model yayımlanmamıştır; kalite kapıları geçilmeden hiçbir ara sonuç başarı ilan edilmez.
