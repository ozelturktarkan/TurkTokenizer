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


## Syntax E02 and interrupted E03 attempt

Syntax E02 completed from the verified E01 state:

- TRAIN loss: `1.5350`
- CALIB syntax loss: `1.5072`
- UAS: `0.81588642`
- LAS: `0.67939617`
- UPOS: `0.88830982`
- selection score: `0.74123461`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

An E03 invocation was interrupted before the epoch boundary. It emitted no E03 metric or state and is not accepted as a result. The active and durable state hashes remained identical at completed epoch 2, next epoch 3. Both E02 recovery archives were independently re-materialized; all file hashes and the reconstructed resumable-state hash passed. That interrupted invocation remained only a recovery event and did not alter the canonical E02 boundary.


## Syntax E03

Syntax E03 was rerun from the verified E02 state and completed successfully:

- TRAIN loss: `1.2569`
- CALIB syntax loss: `1.3776`
- UAS: `0.83947345`
- LAS: `0.70792524`
- UPOS: `0.89527361`
- selection score: `0.76612454`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

E03 improved the selection score and became the selected syntax checkpoint. The active and durable resume states and selected checkpoints matched byte-for-byte. Both external E03 archives were independently re-materialized; every file checksum passed, and each reconstructed state matched the canonical E03 source hash. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.


## Syntax E04

Syntax E04 completed from the verified E03 state and again improved the locked selection score:

- TRAIN loss: `1.0916`
- CALIB syntax loss: `1.3276`
- UAS: `0.84827927`
- LAS: `0.71381076`
- UPOS: `0.89194896`
- selection score: `0.77196514`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

E04 became the selected syntax checkpoint. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both external E04 archives were independently re-materialized; all file checksums passed and each reconstructed state matched the canonical source hash. Sealed evaluation remains unopened.


## Syntax E05 milestone

The precommitted fifth-epoch milestone completed from the verified E04 state:

- TRAIN loss: `0.9803`
- CALIB syntax loss: `1.3306`
- UAS: `0.85528799`
- LAS: `0.72670500`
- UPOS: `0.90237218`
- selection score: `0.78284662`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

CALIB loss rose slightly from E04 while the locked selection score improved, so the overfit signal remained false and E05 became the selected syntax checkpoint. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both milestone E05 archives were independently re-materialized; all file checksums passed and each reconstructed state matched the canonical source hash. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.


## Syntax E06

Syntax E06 completed from the verified E05 milestone state:

- TRAIN loss: `0.8943`
- CALIB syntax loss: `1.3497`
- UAS: `0.85403001`
- LAS: `0.72935574`
- UPOS: `0.90762872`
- selection score: `0.78458532`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

CALIB loss rose again while the locked selection score improved, so the overfit signal remained false and E06 became the selected syntax checkpoint. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both E06 archives were independently re-materialized; every file checksum passed and each reconstructed state matched the canonical source hash. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.


## Syntax E07 and anomaly audit

Syntax E07 completed from the verified E06 state:

- TRAIN loss: `248.4047`
- CALIB syntax loss: `1.3756`
- UAS: `0.85730973`
- LAS: `0.73043400`
- UPOS: `0.90551712`
- selection score: `0.78600503`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The TRAIN-loss jump was reproduced exactly from E06 and isolated to one of 1,242 deterministic batches. That batch's syntax-head loss was `307453.72` with a pre-clip gradient norm of `7464916`; the next-highest batch loss was only `1.7191`. Targets and inputs were valid, attention outputs remained normal, and the activation amplification arose in the Transformer FFN residual path before quadratic amplification by the biaffine head scorer. Gradient clipping at `1.2` bounded the update; no model tensor became non-finite.

The selected E07 checkpoint improved the locked CALIB score. On the affected short TRAIN sentence, evaluation-mode head loss was `0.0105`, and 4,096 fixed-seed dropout stress samples produced maximum head loss `1.4279` with zero samples above `10`. No precommitted stop condition fired. E07 remains the canonical boundary and E08 is authorized under the unchanged protocol with explicit recurrence monitoring. Both E07 state archives and both anomaly-decision archives were independently re-materialized and checksum-verified. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E08

Syntax E08 completed from the verified E07 state:

- TRAIN loss: `1.6368`
- CALIB syntax loss: `2.4491`
- UAS: `0.86427352`
- LAS: `0.74256447`
- UPOS: `0.91050409`
- selection score: `0.79587115`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss spike did not recur. TRAIN loss fell and CALIB loss rose, but the locked selection score improved, so the precommitted overfit signal remained false and E08 became the selected syntax checkpoint. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both E08 archives were independently re-materialized; every file checksum passed and each reconstructed state matched the canonical source. E09 is authorized under the unchanged protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E09

Syntax E09 completed from the verified E08 state:

- TRAIN loss: `0.7453`
- CALIB syntax loss: `1.3295`
- UAS: `0.86252134`
- LAS: `0.74247462`
- UPOS: `0.91198670`
- selection score: `0.79543984`
- patience: `1/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The E07 TRAIN-loss anomaly did not recur. E09 did not improve the locked selection score, so E08 remained the selected syntax checkpoint and patience advanced to `1/9`. The precommitted overfit signal remained false. Active and durable resume states matched, and both E09 archives were independently re-materialized and checksum-verified. Sealed evaluation remained unopened.


## Syntax E10

Syntax E10 completed from the verified E09 state:

- TRAIN loss: `1.7246`
- CALIB syntax loss: `1.3537`
- UAS: `0.86319526`
- LAS: `0.74054273`
- UPOS: `0.91014467`
- selection score: `0.79429868`
- patience: `2/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The E07 anomaly again did not recur. E10 did not improve the locked selection score, so E08 remained selected and patience advanced to `2/9`. CALIB loss rose, but TRAIN loss did not fall, so the precommitted overfit signal remained false. Active and durable resume states matched, and both E10 archives were independently re-materialized and checksum-verified. Sealed evaluation remained unopened.


## Syntax E11

Syntax E11 completed from the verified E10 state:

- TRAIN loss: `0.6764`
- CALIB syntax loss: `1.2991`
- UAS: `0.86499236`
- LAS: `0.74189056`
- UPOS: `0.91396352`
- selection score: `0.79602839`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

E11 improved the locked selection score and became the selected syntax checkpoint. The E07 TRAIN-loss anomaly did not recur, the precommitted overfit signal remained false, and patience reset to `0/9`. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both E11 archives were independently re-materialized; every file checksum passed and each reconstructed state matched the canonical source. E12 is authorized under the unchanged protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E12

Syntax E12 completed from the verified E11 state:

- TRAIN loss: `0.7065`
- CALIB syntax loss: `1.3787`
- UAS: `0.86921556`
- LAS: `0.74916884`
- UPOS: `0.91499686`
- selection score: `0.80176566`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

E12 improved the locked selection score and became the selected syntax checkpoint. The E07 TRAIN-loss anomaly did not recur. CALIB loss rose, but TRAIN loss did not fall, so the precommitted overfit signal remained false and patience stayed at `0/9`. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both E12 archives were independently re-materialized; every file checksum passed and each reconstructed state matched the canonical source. E13 is authorized under the unchanged protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E13

Syntax E13 completed from the verified E12 state:

- TRAIN loss: `0.6212`
- CALIB syntax loss: `1.3917`
- UAS: `0.87060832`
- LAS: `0.75123551`
- UPOS: `0.91778237`
- selection score: `0.80370204`
- patience: `0/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

E13 improved the locked selection score and became the selected syntax checkpoint. The E07 TRAIN-loss anomaly did not recur. TRAIN loss fell and CALIB loss rose, but the improved locked selection score kept the precommitted overfit signal false and patience at `0/9`. Active and durable resume-state/checkpoint pairs matched byte-for-byte. Both E13 archives were independently re-materialized; every file checksum passed and each reconstructed state matched the canonical source. E14 is authorized under the unchanged protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E14

Syntax E14 completed from the verified E13 state:

- TRAIN loss: `1.1213`
- CALIB syntax loss: `1.4219`
- UAS: `0.86845179`
- LAS: `0.74984275`
- UPOS: `0.91423308`
- selection score: `0.80186450`
- patience: `1/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E14 did not improve the locked selection score, so E13 remains the selected syntax checkpoint and patience advanced to `1/9`. CALIB loss rose, but TRAIN loss did not fall, so the precommitted overfit signal remained false. Active and durable E14 resume states matched byte-for-byte. Both E14 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E15 is authorized under the unchanged protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E15

Syntax E15 completed from the verified E14 state:

- TRAIN loss: `0.5821`
- CALIB syntax loss: `1.3974`
- UAS: `0.86773295`
- LAS: `0.74705724`
- UPOS: `0.91562584`
- selection score: `0.80011681`
- patience: `2/9`
- learning rate: `0.0005`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E15 did not improve the locked selection score, so E13 remains the selected syntax checkpoint and patience advanced to `2/9`. TRAIN loss and CALIB syntax loss both fell from E14, so the precommitted overfit signal remained false. Active and durable E15 resume states matched byte-for-byte. Both E15 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E16 is authorized under the unchanged protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E16

Syntax E16 completed from the verified E15 state:

- TRAIN loss: `0.5622`
- CALIB syntax loss: `1.4020`
- UAS: `0.86723875`
- LAS: `0.74961811`
- UPOS: `0.91742295`
- selection score: `0.80168479`
- patience: `3/9`
- learning rate: `0.0005`
- syntax overfit streak: `1/3`

The isolated E07 TRAIN-loss anomaly did not recur. E16 did not improve the locked selection score, so E13 remains the selected syntax checkpoint and patience advanced to `3/9`. TRAIN loss fell while CALIB syntax loss rose beyond the precommitted relative threshold, producing the first consecutive overfit signal (`1/3`); no safety stop fired. Active and durable E16 resume states matched byte-for-byte. Both E16 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E17 is authorized under the unchanged protocol with explicit overfit-recurrence and plateau-LR transition monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E17

Syntax E17 completed from the verified E16 state:

- TRAIN loss: `0.6151`
- CALIB syntax loss: `1.4050`
- UAS: `0.87069818`
- LAS: `0.74831521`
- UPOS: `0.91670411`
- selection score: `0.80186899`
- patience: `4/9`
- learning rate: `0.00025`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E17 did not improve the locked selection score, so E13 remains the selected syntax checkpoint and patience advanced to `4/9`. The deterministic plateau rule therefore reduced the learning rate from `0.0005` to `0.00025`. CALIB syntax loss rose, but TRAIN loss did not fall, so the consecutive overfit signal reset from `1/3` to `0/3`; no safety stop fired. Active and durable E17 resume states matched byte-for-byte. Both E17 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E18 is authorized under the reduced learning rate with the unchanged one-epoch protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E18

Syntax E18 completed from the verified E17 state under the reduced learning rate:

- TRAIN loss: `0.4653`
- CALIB syntax loss: `1.4752`
- UAS: `0.88035762`
- LAS: `0.76332105`
- UPOS: `0.92146644`
- selection score: `0.81424656`
- patience: `0/9`
- learning rate: `0.00025`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E18 improved the locked selection score, replaced E13 as the selected syntax checkpoint, and reset patience from `4/9` to `0/9`. TRAIN loss fell and CALIB syntax loss rose, but the improved selection score kept the precommitted overfit signal false at `0/3`; no safety stop fired. Active and durable E18 resume-state/checkpoint pairs matched byte-for-byte. Both E18 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E19 is authorized under the reduced learning rate and unchanged one-epoch protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E19

Syntax E19 completed from the verified E18 state under the reduced learning rate:

- TRAIN loss: `0.3990`
- CALIB syntax loss: `1.4273`
- UAS: `0.87977356`
- LAS: `0.76242250`
- UPOS: `0.92119687`
- selection score: `0.81350526`
- patience: `1/9`
- learning rate: `0.00025`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E19 did not improve the locked selection score, so E18 remains the selected syntax checkpoint and patience advanced to `1/9`. TRAIN loss and CALIB syntax loss both fell from E18, so the precommitted overfit signal remained false at `0/3`; no safety stop fired. Active and durable E19 resume states matched byte-for-byte, while the selected E18 checkpoint remained unchanged and mirrored. Both E19 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E20 is authorized under the reduced learning rate and unchanged one-epoch protocol. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E20

Syntax E20 completed from the verified E19 state under the reduced learning rate:

- TRAIN loss: `0.3469`
- CALIB syntax loss: `1.5723`
- UAS: `0.88008806`
- LAS: `0.76264714`
- UPOS: `0.92254470`
- selection score: `0.81386917`
- patience: `2/9`
- learning rate: `0.00025`
- syntax overfit streak: `1/3`

The isolated E07 TRAIN-loss anomaly did not recur. E20 did not improve the locked selection score, so E18 remains the selected syntax checkpoint and patience advanced to `2/9`. TRAIN loss fell while CALIB syntax loss rose beyond the precommitted relative threshold, producing the first consecutive overfit signal (`1/3`); no safety stop fired. Active and durable E20 resume states matched byte-for-byte, while the selected E18 checkpoint remained unchanged and mirrored. Both E20 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E21 is authorized under the reduced learning rate and unchanged one-epoch protocol with explicit overfit-recurrence monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E21

Syntax E21 completed from the verified E20 state under the reduced learning rate:

- TRAIN loss: `0.3291`
- CALIB syntax loss: `1.5498`
- UAS: `0.87941414`
- LAS: `0.76296163`
- UPOS: `0.92276934`
- selection score: `0.81387816`
- patience: `3/9`
- learning rate: `0.00025`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E21 did not improve the locked selection score, so E18 remains the selected syntax checkpoint and patience advanced to `3/9`. TRAIN loss and CALIB syntax loss both fell from E20, so the consecutive overfit signal reset from `1/3` to `0/3`; no safety stop fired. Active and durable E21 resume states matched byte-for-byte, while the selected E18 checkpoint remained unchanged and mirrored. Both E21 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E22 is authorized under the reduced learning rate and unchanged one-epoch protocol with continued overfit-recurrence monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E22

Syntax E22 completed from the verified E21 state:

- TRAIN loss: `0.3116`
- CALIB syntax loss: `1.5587`
- UAS: `0.87905472`
- LAS: `0.76138916`
- UPOS: `0.92205050`
- selection score: `0.81275496`
- patience: `4/9`
- learning rate: `0.000125`
- syntax overfit streak: `1/3`

The isolated E07 TRAIN-loss anomaly did not recur. E22 did not improve the locked selection score, so E18 remains the selected syntax checkpoint and patience advanced to `4/9`. The deterministic plateau rule reduced the learning rate from `0.00025` to `0.000125`. TRAIN loss fell while CALIB syntax loss rose beyond the precommitted relative threshold, producing the first consecutive overfit signal after E21's reset (`1/3`); no safety stop fired. Active and durable E22 resume states matched byte-for-byte, while the selected E18 checkpoint remained unchanged and mirrored. Both E22 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E23 is authorized under the newly reduced learning rate and unchanged one-epoch protocol with explicit overfit-recurrence monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E23

Syntax E23 completed from the verified E22 state under the reduced learning rate:

- TRAIN loss: `0.2611`
- CALIB syntax loss: `1.6341`
- UAS: `0.88193009`
- LAS: `0.76300656`
- UPOS: `0.92106209`
- selection score: `0.81448917`
- patience: `0/9`
- learning rate: `0.000125`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E23 improved the locked selection score, replaced E18 as the selected syntax checkpoint, and reset patience from `4/9` to `0/9`. TRAIN loss fell and CALIB syntax loss rose, but the improved selection score kept the precommitted overfit signal false and reset its streak from `1/3` to `0/3`; no safety stop fired. Active and durable E23 resume-state/checkpoint pairs matched byte-for-byte. Both E23 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E24 is authorized under learning rate `0.000125` and the unchanged one-epoch protocol with continued overfit-recurrence monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E24

Syntax E24 completed from the verified E23 state under learning rate `0.000125`:

- TRAIN loss: `0.6463`
- CALIB syntax loss: `1.7110`
- UAS: `0.88193009`
- LAS: `0.76462396`
- UPOS: `0.92335340`
- selection score: `0.81568874`
- patience: `0/9`
- learning rate: `0.000125`
- syntax overfit streak: `0/3`

The isolated E07 TRAIN-loss anomaly did not recur. E24 improved the locked selection score, replaced E23 as the selected syntax checkpoint, and kept patience at `0/9`. TRAIN loss and CALIB syntax loss both rose from E23, so the precommitted overfit signal remained false at `0/3`; no safety stop fired. Active and durable E24 resume-state/checkpoint pairs matched byte-for-byte. Both E24 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E25 is authorized under learning rate `0.000125` and the unchanged one-epoch protocol with continued anomaly and overfit monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E25

Syntax E25 completed from the verified E24 state under learning rate `0.000125`:

- TRAIN loss: `0.2628`
- CALIB syntax loss: `1.7332`
- UAS: `0.88228951`
- LAS: `0.76403990`
- UPOS: `0.92308384`
- selection score: `0.81541918`
- patience: `1/9`
- learning rate: `0.000125`
- syntax overfit streak: `1/3`

The isolated E07 TRAIN-loss anomaly did not recur. E25 did not improve the locked selection score, so E24 remains the selected syntax checkpoint and patience advanced from `0/9` to `1/9`. TRAIN loss fell while CALIB syntax loss rose beyond the precommitted relative threshold, producing the first consecutive overfit signal (`1/3`); no safety stop fired and the learning rate was not reduced. Active and durable E25 resume states matched byte-for-byte, while the selected E24 checkpoint remained unchanged and mirrored. Both E25 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E26 is authorized under learning rate `0.000125` and the unchanged one-epoch protocol with explicit overfit-streak monitoring. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Syntax E26

Syntax E26 completed from the verified E25 state under learning rate `0.000125`:

- TRAIN loss: `0.2110`
- CALIB syntax loss: `1.7778`
- UAS: `0.88188516`
- LAS: `0.76403990`
- UPOS: `0.92357804`
- selection score: `0.81534729`
- patience: `2/9`
- learning rate: `0.000125`
- syntax overfit streak: `2/3`

The isolated E07 TRAIN-loss anomaly did not recur. E26 did not improve the locked selection score, so E24 remains the selected syntax checkpoint and patience advanced from `1/9` to `2/9`. TRAIN loss fell while CALIB syntax loss again rose beyond the precommitted relative threshold, extending the consecutive overfit signal from `1/3` to `2/3`; no safety stop fired and the learning rate was not reduced. Active and durable E26 resume states matched byte-for-byte, while the selected E24 checkpoint remained unchanged and mirrored. Both E26 archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and all archived files matched their source bytes. E27 is authorized under learning rate `0.000125` and the unchanged one-epoch protocol; the precommitted safety stop will fire if the same overfit condition recurs for a third consecutive epoch. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.
