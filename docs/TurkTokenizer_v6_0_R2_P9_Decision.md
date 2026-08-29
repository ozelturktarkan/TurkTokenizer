# TurkTokenizer v6.0 R2-P9 public decision note

R2-P9 repairs the morphology lattice and resumes the fixed-seed TRAIN/CALIB screen from the selected Syntax E20 boundary. The migration preserves compatible model and optimizer rows by serialized vocabulary symbol rather than by row position.

## Accepted changes

- Syntax, relation, and hard-negative epoch ceilings are all 50.
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

The latest independently archived resume boundary is Syntax E21, with the next epoch set to E22 and patience at `1/9`. Live TRAIN/CALIB metrics are preliminary and are not a final model-quality claim.

Datasets, serialized lattices, checkpoints, optimizer state, private hashes, and sealed-split metadata remain outside the public repository.
