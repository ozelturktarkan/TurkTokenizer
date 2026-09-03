# TurkTokenizer v6.1 R4-P1 precommit

Status: `PRECOMMITTED_BEFORE_FIRST_OPTIMIZER_STEP`

R4-P1 asks whether the repaired-lattice R2 architecture can be reconstructed reproducibly from a fresh initialization before family adapters, PCGrad, or ranking loss are introduced.

## Locked delta

- Fresh seed-`51104` initialization.
- Fresh syntax training on the repaired morphology lattice.
- Existing R2 focal objective and architecture.
- No R2-P9, R1, or R3 checkpoint migration.
- No family adapter.
- No PCGrad.
- No ranking loss.

R4-P1 is a parent reconstruction, not a promotion claim. Its final metrics become the matched focal baseline for R4-P2.

## Training policy

| Stage | Epoch ceiling | Patience | Initial learning rate |
|---|---:|---:|---:|
| Syntax | 70 | 9 | 0.0005 |
| Relation | 50 | 9 | 0.00025 |
| Hard-negative | 50 | 9 | 0.00012 |

A selection improvement must exceed `0.0001`. The learning rate is halved once when a stage first reaches four consecutive non-improving epochs.

Syntax also has the locked three-epoch safety guard: selection score must not improve, TRAIN loss must fall, and CALIB syntax loss must rise by at least 0.1% in each qualifying epoch. The selected syntax checkpoint is frozen when that streak reaches three.

Batch size is 24. The morphology top-k remains 20. All model widths, dropout, loss weights, threshold grids, and source hard-negative warmup settings remain inherited from the repaired-lattice R2 configuration.

## Interruption and persistence

Every completed epoch is atomically recorded in an active state file and a second local durable mirror, including the model, optimizer, RNG, sampler position, best score, patience state, effective learning rate, and syntax overfit state.

External A/B archives are required at precommit, start gate, the first epoch, every fifth epoch, every stage completion or safety stop, and final closure. Each final archive must be independently re-materialized and SHA-256 verified.

## Parent exit conditions

R4-P1 becomes `PARENT_READY` only if:

- smoke and start gate pass before the first optimizer step;
- all three stages stop only under their locked ceiling, patience, or syntax safety rule;
- the selected checkpoint and final CALIB screen are emitted;
- two independent final screen executions on the unchanged selected checkpoint match exactly;
- both closure packages pass independent checksum verification;
- no adapter, PCGrad, ranking loss, or migrated checkpoint is used.

CALIB is authorized only for checkpoint selection and screening. `INTERNAL_VAL`, external BOUN/IMST/Penn holdouts, and official TEST remain sealed.

R4-P2 may be precommitted only after every P1 parent-exit condition is satisfied.
