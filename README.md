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

- `src/`: frozen analyzer, runtime tokenizer, corpus verifier, locked v4 trainer, and v4.1 ablation drivers.
- `contracts/`: architecture, provenance, conservation, and ablation precommits.
- `audits/`: public-safe aggregate CALIB, smoke, screen, and build reports.
- `docs/`: decision reports and completed A1/A2 training logs.
- `project_state/`: current machine-readable ledger.
- `data/`: acquisition and seal policy; no datasets are redistributed here.

Some files are duplicated beside the training scripts because the sealed research drivers intentionally resolve locked dependencies relative to their own directory.

## Reproduction outline

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Acquire the exact corpus blobs described in `contracts/TurkTokenizer_v5_11_v4_Corpus_Provenance_Precommit.json`, then verify only the training-pool role:

```bash
python src/TurkTokenizer_v5_11_v4_verify_corpora.py \
  --directory data/corpora_exact \
  --manifest src/TurkTokenizer_v5_11_v4_Corpus_Provenance_Precommit.json \
  --runtime src/TurkTokenizer_v5_11_v4_RuntimeTokens.py \
  --roles V4_TRAINING_POOL \
  --output src/TurkTokenizer_v5_11_v4_Corpus_Local_Audit.json
```

Build the locked split and training artifacts:

```bash
python src/TurkTokenizer_v5_11_v4_build_data.py \
  --corpora data/corpora_exact \
  --manifest src/TurkTokenizer_v5_11_v4_Corpus_Provenance_Precommit.json \
  --audit src/TurkTokenizer_v5_11_v4_Corpus_Local_Audit.json \
  --runtime src/TurkTokenizer_v5_11_v4_RuntimeTokens.py \
  --morphology src/bases/TurkTokenizer_v5_5_4_FROZEN.py
```

The A3 candidate-space sequence is:

```bash
python src/TurkTokenizer_v5_11_v4_1_A3_build_coverage_lattice.py
python src/TurkTokenizer_v5_11_v4_1_A3_coverage_audit.py
python src/TurkTokenizer_v5_11_v4_1_A3_train.py --smoke
python src/TurkTokenizer_v5_11_v4_1_A3_train.py --screen
```

The screen command is intentionally expensive. Before running it, verify hashes against the A3 precommit and arrange durable checkpoint/log storage. Do not add evaluation data to Git.

## License and data

Code and repository-authored documentation are licensed under Apache-2.0. Third-party corpora retain their own licenses and are not covered by this repository's license. See [data/README.md](data/README.md).

## Türkçe özet

Bu depo; Türkçenin sondan eklemeli yapısını, ek-kök ilişkilerini, ünlü uyumlarını, ses olaylarını ve sözdizimsel ilişkilerini kayıpsız yüzey tokenlarıyla birlikte modellemeyi hedefleyen açık araştırma projesidir. Henüz nihai model yayımlanmamıştır; kalite kapıları geçilmeden hiçbir ara sonuç başarı ilan edilmez.
