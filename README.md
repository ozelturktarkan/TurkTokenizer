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
| v4.1 A3 coverage repair | Coverage gate passed; training incomplete | — | — | — | — |
| v6.0 R2-P9 repair | Drop after screen | 0.8020 | 0.7121 | 0.8843 | 0.7654 |
| v6.0 R2-P10 decoupled decision | Drop after screen | 0.8018 | 0.7141 | 0.8843 | 0.7654 |
| v6.0 R3-P1 R1 null-arc decision | Drop after screen | 0.8051 | 0.7118 | 0.8831 | 0.7643 |
| v6.0 R3-P2 paired ranking-loss ablation | Running; candidate Relation complete, Hard-Negative E15 persisted | — | — | — | — |

The v6.0 R2-P9 repair line restored the selected Syntax E20 boundary with a repaired morphology lattice, conflict-aware source supervision, a Syntax E70 ceiling, Relation/Hard-Negative E50 ceilings, and patience 9 for all three stages. Syntax closed at E42 with E38 selected, Relation closed at E37 with E28 selected, and Hard-Negative closed at H21 with H12 selected. The final TRAIN/CALIB screen yielded macro F1 `0.8020`, minimum-family F1 `0.7121`, `UAS=0.8843`, and `LAS=0.7654`; the precommitted decision is `DROP_AFTER_SCREEN`. Sealed evaluation remains unopened. See [the R2-P9 decision note](docs/TurkTokenizer_v6_0_R2_P9_Decision.md).

A CALIB-only A1–R1–H21 error decomposition found that H21 improves OBJECT source discrimination and head ranking separately, but the product-coupled direct-edge score does not retain those gains. R2-P10 froze the model and changed only the direct-relation activation score. It improved OBJECT F1 by `+0.0020` over H21 but remained below A1 and slightly reduced macro F1, so the precommitted decision is `DROP_AFTER_SCREEN`. See [the R2-P10 decision](docs/TurkTokenizer_v6_0_R2_P10_Decision.md).

R3-P1 returned to the frozen R1 null-arc checkpoint and changed only the direct-relation activation score. Source-only activation reduced OBJECT and macro F1 versus R1, so every promotion gate except the unchanged CASE_GOVERNOR policy failed. The precommitted decision is `DROP_AFTER_SCREEN`; post-hoc decision rescue is closed. See [the R3-P1 decision](docs/TurkTokenizer_v6_0_R3_P1_Decision.md).

R3-P2 is running as a paired TRAIN/CALIB loss ablation. The control arm is
complete. Candidate Relation reached its precommitted E50 ceiling with the
selected checkpoint, completion marker, local mirror, and two persistent
packages verified. Candidate Hard-Negative E15 completed with its active and
durable states plus two persistent packages verified. The R1 decoder and
inference rule stay fixed, and only the direct-family training loss changes
from joint focal likelihood to zero-margin hardest-competitor ranking. Arm
metrics remain blinded until the candidate arm also closes, and sealed
evaluation stays unopened. See [the R3-P2 precommit](docs/TurkTokenizer_v6_0_R3_P2_Precommit.md)
and [candidate progress](docs/TurkTokenizer_v6_0_R3_P2_Candidate_Progress.md).

A3 reached syntax epoch 12 and relation epoch 3 before the active workspace was interrupted while relation epoch 4 was computing. The last complete relation snapshot was provisional (`macro=0.7860`, `minimum/OBJECT=0.7019`, `UAS=0.8705`, `LAS=0.7434`) and is not a final A3 result. It must not be compared as if the screen or hard-negative stage had completed.

The authoritative current state is [STATUS.md](STATUS.md) and [TurkTokenizer_v5_11_Quality_Ledger_v4.json](project_state/TurkTokenizer_v5_11_Quality_Ledger_v3.json).

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
