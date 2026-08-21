# Data and evaluation policy

This repository does not redistribute corpora, serialized split packages, morphology lattices, checkpoints, or sealed evaluation resources.

The locked v4 gradient pool is composed of the official TRAIN files for:

- [UD Turkish Kenet](https://github.com/UniversalDependencies/UD_Turkish-Kenet)
- [UD Turkish Tourism](https://github.com/UniversalDependencies/UD_Turkish-Tourism)
- [UD Turkish Atis](https://github.com/UniversalDependencies/UD_Turkish-Atis)
- [UD Turkish FrameNet](https://github.com/UniversalDependencies/UD_Turkish-FrameNet)

BOUN, IMST, and Penn are corpus-level external holdouts. Official TEST files are not part of v4 training or CALIB selection.

Use the exact filenames and Git blob SHA values in `contracts/TurkTokenizer_v5_11_v4_Corpus_Provenance_Precommit.json`. The verifier aborts on a blob mismatch and selects `V4_TRAINING_POOL` roles by default. Each dataset remains subject to its upstream license and attribution requirements.

Never commit any of the following:

- `.conllu`, `.pkl`, `.pt`, `.pth`, or `.ckpt` files;
- `INTERNAL_VAL` material or its labels/metrics before an eligible one-time gate opening;
- BOUN/IMST/Penn-derived labels or official TEST outputs before the Phase-5 protocol permits them;
- corpus-derived example dumps when aggregate metrics are sufficient.
