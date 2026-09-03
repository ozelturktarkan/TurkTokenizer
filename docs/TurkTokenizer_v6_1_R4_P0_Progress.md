# TurkTokenizer v6.1 R4-P0 progress

## Final state

R4-P0 is complete and passed.

The smoke gate, start gate, and the precommitted 12-batch TRAIN-only gradient-conflict audit all completed successfully:

- all locked inputs matched;
- a fresh repaired-lattice `R2Model` was initialized without a checkpoint;
- all six primitive task losses and gradients remained finite;
- exactly 12 balanced batches of 24 examples completed at seed `51104`;
- no optimizer was instantiated and optimizer steps remained zero;
- the model-state digest was unchanged;
- CALIB was absent from the workspace;
- `INTERNAL_VAL`, external holdouts, and official TEST remained unopened.

## Fixed routing result

The P2 routing contract applies deterministic PCGrad to three eligible shared groups:

| Shared group | Conflicted task pairs |
|---|---:|
| shared Transformer | 7 |
| relation bridge | 3 |
| syntax bridge | 5 |

The strongest routed mean conflict was `POSS_HEAD ↔ OBJECT` in the syntax bridge (mean cosine `-0.0230`; negative in 7/12 batches). The lexical/morphological block also produced recorded conflicts, but it was not PCGrad-eligible under the precommitted runner and remains unchanged.

The adapter contract remains fixed at post-graph/pre-family scoring with bottleneck 48, LayerNorm plus GELU, residual-gate initial logit `-2.0`, and a total new-parameter ceiling of 200,000.

Both final P0 packages were independently re-materialized and checksum-verified. R4-P1 may now be precommitted as a fresh repaired-lattice reconstruction with no adapter, no PCGrad, and no checkpoint migration. See the [decision note](TurkTokenizer_v6_1_R4_P0_Decision.md).
