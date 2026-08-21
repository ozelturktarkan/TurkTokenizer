# TurkTokenizer

TurkTokenizer is an open research project for lossless Turkish tokenization, morphology-aware candidate generation, and morphosyntactic relation graphs. The current v5.11 line combines raw surface tokens, a Unicode character encoder, a frozen top-20 morphology lattice, an eight-layer relative-position Transformer, dependency structure, and specialized relation experts.

This repository is a research snapshot, not a production release. Reported scores are CALIB-only architecture-selection results. The sealed `INTERNAL_VAL`, external BOUN/IMST/Penn holdouts, official TEST splits, corpus files, derived `.pkl` packages, and model checkpoints are not included.

## Current state

### Live v6.0 R2 E50 screen

A fresh fixed-seed R2 source-first screen is running on TRAIN/CALIB only. The
maximum epoch budget is `50` for syntax, relation, and hard-negative stages;
early stopping remains bounded at five consecutive non-improving completed
epochs. An improvement greater than `1e-4` writes a new best checkpoint and
resets patience to `0/5`.

Syntax epoch 22 completed with selection score `0.80437146`
(`UAS=0.8751`, `LAS=0.7501`, `UPOS=0.9179`). It did not exceed the epoch-20
best score `0.80719741`, so that checkpoint remains selected and patience is
`2/5`.
The public-safe machine-readable progress record is
[TurkTokenizer_v6_0_R2_E50_Live_Status.json](project_state/TurkTokenizer_v6_0_R2_E50_Live_Status.json).
`INTERNAL_VAL`, external BOUN/IMST/Penn holdouts, and official TEST splits
remain unopened.

| Line | Decision | Macro F1 | Minimum-family F1 | UAS | LAS |
|---|---:|---:|---:|---:|---:|
| v3S BiLSTM | Rejected before `INTERNAL_VAL` | 0.7606 | 0.6291 | — | — |
| v4 locked baseline | Rejected before `INTERNAL_VAL` | 0.7972 | 0.7025 | 0.8752 | 0.7552 |
| v4.1 A1 contextual posterior | Keep for finalist screening; absolute gates failed | 0.8108 | 0.7174 | 0.8785 | 0.7599 |
| v4.1 A2 ordered realizations | Drop after screen | 0.8061 | 0.6918 | 0.8769 | 0.7602 |
| v4.1 A3 coverage repair | Coverage gate passed; training incomplete | — | — | — | — |

A3 reached syntax epoch 12 and relation epoch 3 before the active workspace was interrupted while relation epoch 4 was computing. The last complete relation snapshot was provisional (`macro=0.7860`, `minimum/OBJECT=0.7019`, `UAS=0.8705`, `LAS=0.7434`) and is not a final A3 result. It must not be compared as if the screen or hard-negative stage had completed.

The authoritative current state is [STATUS.md](STATUS.md) and [TurkTokenizer_v5_11_Quality_Ledger_v3.json](project_state/TurkTokenizer_v5_11_Quality_Ledger_v3.json).

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
