# TurkTokenizer v6.0 R2-P9 public decision note

R2-P9 repairs the morphology lattice and resumes the fixed-seed TRAIN/CALIB screen from the selected Syntax E20 boundary. The migration preserves compatible model and optimizer rows by serialized vocabulary symbol rather than by row position.

## Accepted changes

- The Syntax epoch ceiling is 70; Relation and Hard-Negative epoch ceilings are 50.
- Patience is 9 in all three stages and resets to `0/9` after a qualifying improvement above `best + 0.0001`.
- The learning rate is halved at the fourth consecutive non-improving epoch and remains in optimizer state.
- Ambiguous source supervision uses conflict-aware focal balancing.
- Hard-negative source penalty uses a three-epoch warmup.
- Numeric, apostrophe-bearing, and other vowelless surfaces no longer raise the previous `NoneType` vowel-harmony exception.

The proposed source-filter width increase was rejected because annotation conflict is not evidence of insufficient layer capacity and the width change would invalidate the E20 architecture.

## Public-safe validation

- Previous morphology exception surfaces: 883
- Current morphology exception surfaces: 0
- Morphology candidates added: 3,231
- Architecture smoke test: pass
- Finite losses and gradients: pass
- Invalid morphology masks: safe
- Sealed evaluation consumed: false

## Final screen closure

- Syntax stopped safely at E42 after the overfitting guard reached `3/3`; E38 remained selected with score `0.81872136`.
- Relation stopped at E37 when patience reached `9/9`; E28 remained selected with score `0.78178072`.
- Hard-Negative stopped at H21 when patience reached `9/9`; H12 remained selected with score `0.78176522`. H21 scored `0.78079397`.
- The final CALIB screen produced macro F1 `0.80204292`, minimum-family F1 `0.71206775`, `UAS=0.88431126`, and `LAS=0.76538773`.
- The precommitted decision is `DROP_AFTER_SCREEN`; `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

The H21 final state and completion marker are retained in two independent private durable packages. Live checkpoints, optimizer state, and private resource fingerprints are not published.

Datasets, serialized lattices, checkpoints, optimizer state, private hashes, and sealed-split metadata remain outside the public repository.
