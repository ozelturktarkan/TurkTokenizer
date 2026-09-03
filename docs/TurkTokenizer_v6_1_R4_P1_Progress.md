# TurkTokenizer v6.1 R4-P1 progress

## Start boundary

R4-P1 is precommitted as a fresh repaired-lattice parent reconstruction. Its private precommit packages were independently re-materialized and checksum-verified before execution.

The smoke test and start gate passed:

- 29,741,930 parameters;
- finite syntax and relation losses and gradients;
- repaired-lattice posteriors valid;
- seed `51104`, batch size 24, ceilings 70/50/50, and patience 9/9/9 matched the precommit;
- the fresh initial model digest was recorded;
- no resume state or model checkpoint existed;
- checkpoint migration, adapters, PCGrad, and ranking loss were disabled;
- `INTERNAL_VAL`, external holdouts, and official TEST remained unopened.

Both start-gate packages were independently re-materialized and checksum-verified. Fresh Syntax E01 is authorized to begin under one-epoch interruption-safe execution. CALIB is used only for the locked checkpoint-selection measurements.


## Syntax E01

Syntax E01 completed at the first interruption-safe boundary:

- TRAIN loss: `2.5446`
- CALIB syntax loss: `1.7081`
- UAS: `0.7679`
- LAS: `0.6322`
- UPOS: `0.8698`
- selection score: `0.69667086`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The selected checkpoint and full resumable state matched their local durable mirrors. The state was split into seven ordered parts; both external E01 archives were independently re-materialized, every file checksum passed, and the reconstructed state hash matched the source. E02 is the next authorized boundary.
