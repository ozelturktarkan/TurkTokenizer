# TurkTokenizer v6.1 R4-P0 precommit

Status: `PRECOMMITTED_BEFORE_EXECUTION`

R4-P0 is a zero-update, TRAIN-only gradient-conflict audit. It does not train or select a checkpoint. Its purpose is to identify which primitive task gradients conflict on a fresh repaired-lattice R2 architecture and to freeze the routing contract used by later R4 phases.

## Locked execution

- Fresh deterministic `R2Model` initialization; no R2-P9, R1, or R3 checkpoint is loaded.
- Seed: `51104`.
- Sampler: `BalancedTreebankBatchSampler`, epoch 0.
- Exactly 12 TRAIN batches of 24 examples.
- No optimizer is instantiated and optimizer steps remain zero.
- CALIB is absent from the workspace; `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.
- The model-state digest must be identical before and after the audit.

The six primitive losses are `SYNTAX_STRUCTURAL`, `MORPH_CONTEXT`, `POSS_HEAD`, `OBJECT`, `PARTICIPLE_HEAD`, and `CASE_GOVERNOR`. Hard-negative training is outside P0.

## Gradient scope and conflict rule

Family-owned scorer modules are excluded from the shared-gradient audit. Shared parameters are reported as lexical/morphological, shared Transformer, syntax bridge, relation bridge, and other shared groups.

For every task pair and shared group, P0 records cosine mean, minimum, maximum, and the fraction of batches with negative cosine. A pair is precommitted as conflicted when either:

- mean cosine is below `-0.02`; or
- the negative-batch fraction is at least `0.50`.

The emitted routing map is deterministic. PCGrad projects only negative pairwise dot products and is applied only to shared groups that satisfy the conflict rule. Family-owned modules receive only their owner-family loss.

## Later-phase boundary

The bounded adapter contract is locked before training: one adapter per direct family, inserted after graph composition and before family scoring; bottleneck width 48; LayerNorm plus GELU; residual-gate initial logit `-2.0`; at most 200,000 new parameters.

R4-P1 may start only after the P0 smoke, start gate, full audit, duplicate persistence, and public status update are complete. P1 is a fresh repaired-lattice reconstruction with no adapters and no PCGrad. R4-P2 may add only the precommitted routing and family adapters, R4-P3 may add ranking loss only if P2 passes, and R4-P4 is a three-seed confirmation using seeds `51104`, `62117`, and `73129`.

## Pass conditions

P0 passes only if all locked inputs match, every loss and gradient is finite, exactly 12 deterministic TRAIN batches complete, the model state remains unchanged, the fixed routing map is emitted, and CALIB remains absent.

Private input hashes, split inventories, serialized data, and executable training artifacts remain outside the public repository.
