# TurkTokenizer v6.1 R4-P0 progress

## Start boundary

The R4-P0 precommit is public and the corresponding private executable package was written twice, independently re-materialized, and checksum-verified.

The TRAIN-only smoke gate and start gate both passed:

- all locked inputs matched;
- a fresh repaired-lattice `R2Model` was initialized without a checkpoint;
- all six primitive task losses and gradients were finite;
- no optimizer was instantiated and optimizer steps remained zero;
- the model-state digest was unchanged;
- CALIB was absent from the workspace;
- `INTERNAL_VAL`, external holdouts, and official TEST remained unopened.

The smoke and start-gate outputs were then written to two additional private packages, independently re-materialized, and checksum-verified.

## Active measurement

The precommitted 12-batch TRAIN-only gradient-conflict audit is now running with seed `51104`, balanced batch size 24, and the fixed task order documented in the [R4-P0 precommit](TurkTokenizer_v6_1_R4_P0_Precommit.md).

No audit result or routing conclusion is reported until all 12 batches complete, the model-state digest is rechecked, and both final packages pass independent checksum verification.
