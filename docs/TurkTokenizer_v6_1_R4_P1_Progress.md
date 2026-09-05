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

## Syntax E27

Syntax E27 completed from the verified E26 state under learning rate `0.000125`:

- TRAIN loss: `0.2003`
- CALIB syntax loss: `1.8357`
- UAS: `0.88188516`
- LAS: `0.76475874`
- UPOS: `0.92196064`
- selection score: `0.81561686`
- patience: `3/9`
- learning rate: `0.000125`
- syntax overfit streak: `3/3`

The isolated E07 TRAIN-loss anomaly did not recur. E27 did not improve the locked selection score, so E24 remains the selected syntax checkpoint and patience advanced from `2/9` to `3/9`. TRAIN loss fell while CALIB syntax loss rose beyond the precommitted relative threshold for a third consecutive epoch, so the overfit guard reached `3/3` and the precommitted safety stop fired. The selected E24 checkpoint was copied to the frozen Syntax checkpoint, and both the safety marker and Syntax completion marker were persisted. Active and durable E27 state, selected checkpoint, frozen checkpoint, and closure markers matched byte-for-byte. Both 21-file E27 closure archives were independently re-materialized; every file checksum passed, each reconstructed state matched the canonical source, and the selected and frozen checkpoints matched their source bytes. Syntax is closed safely at E27; Syntax E28 is not authorized, and any later stage requires a separate continuation decision. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E01

Relation E01 started cleanly from the frozen selected Syntax E24 parent after the verified E27 Syntax safety closure:

- combined TRAIN loss: `0.5197`
- macro relation F1: `0.78168849`
- minimum-family F1: `0.67187500` (`OBJECT`)
- `POSS_HEAD` F1: `0.76209279`
- `OBJECT` F1: `0.67187500`
- `PARTICIPLE_HEAD` F1: `0.82978723`
- `CASE_GOVERNOR` F1: `0.86299892`
- UAS: `0.87254021`
- LAS: `0.75083116`
- UPOS: `0.91661425`
- selection score: `0.75714697`
- patience: `0/9`
- learning rate: `0.00025`

The runner recognized the completed Syntax stage and restored the selected E24 checkpoint rather than the overfit E27 model state. E01 established the first Relation checkpoint and therefore reset/kept patience at `0/9`; no learning-rate reduction occurred. The active and durable Relation state/checkpoint mirrors matched byte-for-byte, and the frozen Syntax parent remained unchanged. Both 21-file Relation E01 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected Relation checkpoint and required Syntax parent checkpoint matched their source bytes. Relation E02 and Hard-Negative were not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E02

Relation E02 completed from the verified E01 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.4583`
- macro relation F1: `0.78736897`
- minimum-family F1: `0.68866962` (`OBJECT`)
- `POSS_HEAD` F1: `0.79666319`
- `OBJECT` F1: `0.68866962`
- `PARTICIPLE_HEAD` F1: `0.81538462`
- `CASE_GOVERNOR` F1: `0.84875847`
- UAS: `0.87361847`
- LAS: `0.75433552`
- UPOS: `0.91895049`
- selection score: `0.76530776`
- patience: `0/9`
- learning rate: `0.00025`

E02 improved the locked Relation selection score and became the selected Relation checkpoint. Patience remained at `0/9`, and no learning-rate reduction occurred. The runner restored the selected Syntax E24 parent, completed only E02, persisted the active and durable Relation mirrors, and stopped at the external-backup boundary before E03. Both 21-file Relation E02 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E02 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E03 and Hard-Negative were not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E03

Relation E03 completed from the verified E02 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.3653`
- macro relation F1: `0.79378718`
- minimum-family F1: `0.69486194` (`OBJECT`)
- `POSS_HEAD` F1: `0.79365079`
- `OBJECT` F1: `0.69486194`
- `PARTICIPLE_HEAD` F1: `0.82785300`
- `CASE_GOVERNOR` F1: `0.85878301`
- UAS: `0.87581993`
- LAS: `0.75420074`
- UPOS: `0.91787223`
- selection score: `0.77086534`
- patience: `0/9`
- learning rate: `0.00025`

E03 improved the locked Relation selection score and became the selected Relation checkpoint. Patience remained at `0/9`, and no learning-rate reduction occurred. The runner completed only E03 and stopped at the external-backup boundary before E04. Both 21-file Relation E03 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E03 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E04 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E04

Relation E04 completed from the verified E03 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.3509`
- macro relation F1: `0.78712298`
- minimum-family F1: `0.69784910` (`OBJECT`)
- `POSS_HEAD` F1: `0.78862559`
- `OBJECT` F1: `0.69784910`
- `PARTICIPLE_HEAD` F1: `0.80817916`
- `CASE_GOVERNOR` F1: `0.85383807`
- UAS: `0.87707790`
- LAS: `0.75649205`
- UPOS: `0.92092731`
- selection score: `0.76807126`
- patience: `1/9`
- learning rate: `0.00025`

E04 did not improve the locked Relation selection score, so E03 remained selected and patience advanced to `1/9`; no learning-rate reduction occurred. The runner completed only E04 and stopped at the external-backup boundary before E05. Both 21-file Relation E04 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E03 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E05 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E05

Relation E05 completed from the verified E04 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.4958`
- macro relation F1: `0.79498227`
- minimum-family F1: `0.71264368` (`OBJECT`)
- `POSS_HEAD` F1: `0.79580153`
- `OBJECT` F1: `0.71264368`
- `PARTICIPLE_HEAD` F1: `0.82583170`
- `CASE_GOVERNOR` F1: `0.84565217`
- UAS: `0.87784167`
- LAS: `0.75635726`
- UPOS: `0.91926498`
- selection score: `0.77667585`
- patience: `0/9`
- learning rate: `0.00025`

E05 improved the locked Relation selection score, became the selected Relation checkpoint, and reset patience from `1/9` to `0/9`; no learning-rate reduction occurred. The runner completed only E05 and stopped at the external-backup boundary before E06. Both 21-file Relation E05 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E05 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E06 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E06

Relation E06 completed from the verified E05 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.2434`
- macro relation F1: `0.79806569`
- minimum-family F1: `0.71158474` (`OBJECT`)
- `POSS_HEAD` F1: `0.79408867`
- `OBJECT` F1: `0.71158474`
- `PARTICIPLE_HEAD` F1: `0.82388664`
- `CASE_GOVERNOR` F1: `0.86270270`
- UAS: `0.87869530`
- LAS: `0.75572828`
- UPOS: `0.91908527`
- selection score: `0.77820258`
- patience: `0/9`
- learning rate: `0.00025`

E06 improved the locked Relation selection score and became the selected Relation checkpoint. Patience remained at `0/9`, and no learning-rate reduction occurred. The runner completed only E06 and stopped at the external-backup boundary before E07. Both 21-file Relation E06 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E06 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E07 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E07

Relation E07 completed from the verified E06 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.2494`
- macro relation F1: `0.80065948`
- minimum-family F1: `0.70238507` (`OBJECT`)
- `POSS_HEAD` F1: `0.80745342`
- `OBJECT` F1: `0.70238507`
- `PARTICIPLE_HEAD` F1: `0.82664055`
- `CASE_GOVERNOR` F1: `0.86615887`
- UAS: `0.87743733`
- LAS: `0.75536886`
- UPOS: `0.92110702`
- selection score: `0.77709727`
- patience: `1/9`
- learning rate: `0.00025`

E07 did not improve the locked Relation selection score, so E06 remained selected and patience advanced to `1/9`; no learning-rate reduction occurred. The runner completed only E07 and stopped at the external-backup boundary before E08. Both 21-file Relation E07 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E06 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E08 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E08

Relation E08 completed from the verified E07 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.2139`
- macro relation F1: `0.79451972`
- minimum-family F1: `0.70163005` (`OBJECT`)
- `POSS_HEAD` F1: `0.78520041`
- `OBJECT` F1: `0.70163005`
- `PARTICIPLE_HEAD` F1: `0.82117882`
- `CASE_GOVERNOR` F1: `0.87006961`
- UAS: `0.87541558`
- LAS: `0.75343697`
- UPOS: `0.91989397`
- selection score: `0.77303539`
- patience: `2/9`
- learning rate: `0.00025`

E08 did not improve the locked Relation selection score, so E06 remained selected and patience advanced to `2/9`; no learning-rate reduction occurred. The runner completed only E08 and stopped at the external-backup boundary before E09. Both 21-file Relation E08 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E06 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E09 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E09 and redundant-invocation audit

Relation E09 completed from the verified E08 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1948`
- macro relation F1: `0.80110980`
- minimum-family F1: `0.71530249` (`OBJECT`)
- `POSS_HEAD` F1: `0.79958463`
- `OBJECT` F1: `0.71530249`
- `PARTICIPLE_HEAD` F1: `0.81331988`
- `CASE_GOVERNOR` F1: `0.87623220`
- UAS: `0.87581993`
- LAS: `0.75505436`
- UPOS: `0.91917513`
- selection score: `0.78069476`
- patience: `0/9`
- learning rate: `0.00025`

Two concurrent E09 invocations were detected during recovery. One ended before emitting an E09 metric or state boundary and contributes no result. The sole accepted E09 boundary was independently re-evaluated and packaged.

E09 improved the locked Relation selection score, replaced E06 as the selected Relation checkpoint, and reset patience from `2/9` to `0/9`; no learning-rate reduction occurred. The accepted runner completed only E09 and stopped at the external-backup boundary before E10. Both 21-file Relation E09 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E09 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E10 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E10

Relation E10 completed from the verified E09 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.2046`
- macro relation F1: `0.80415652`
- minimum-family F1: `0.71280992` (`OBJECT`)
- `POSS_HEAD` F1: `0.81342547`
- `OBJECT` F1: `0.71280992`
- `PARTICIPLE_HEAD` F1: `0.82101167`
- `CASE_GOVERNOR` F1: `0.86937901`
- UAS: `0.88125618`
- LAS: `0.76156887`
- UPOS: `0.91796208`
- selection score: `0.78267977`
- patience: `0/9`
- learning rate: `0.00025`

E10 improved the locked Relation selection score and became the selected Relation checkpoint. Patience remained at `0/9`, and no learning-rate reduction occurred. The runner completed only E10 and stopped at the external-backup boundary. Both 21-file Relation E10 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E10 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. This requested E03–E10 execution window is closed at E10; Relation E11 and Hard-Negative were not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E11

Relation E11 completed from the verified E10 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1857`
- macro relation F1: `0.79863818`
- minimum-family F1: `0.70358090` (`OBJECT`)
- `POSS_HEAD` F1: `0.79556898`
- `OBJECT` F1: `0.70358090`
- `PARTICIPLE_HEAD` F1: `0.82457879`
- `CASE_GOVERNOR` F1: `0.87082405`
- UAS: `0.87680834`
- LAS: `0.75478480`
- UPOS: `0.91715338`
- selection score: `0.77615659`
- patience: `1/9`
- learning rate: `0.00025`

E11 did not improve the locked Relation selection score, so E10 remains the selected Relation checkpoint and patience advanced from `0/9` to `1/9`; no learning-rate reduction occurred. The runner completed only E11 and stopped at the external-backup boundary before E12. Both 21-file Relation E11 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E10 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E12 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E12

Relation E12 completed from the verified E11 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1828`
- macro relation F1: `0.80572525`
- minimum-family F1: `0.70905321` (`OBJECT`)
- `POSS_HEAD` F1: `0.80434783`
- `OBJECT` F1: `0.70905321`
- `PARTICIPLE_HEAD` F1: `0.83573487`
- `CASE_GOVERNOR` F1: `0.87376509`
- UAS: `0.88098661`
- LAS: `0.75981670`
- UPOS: `0.92020846`
- selection score: `0.78243111`
- patience: `2/9`
- learning rate: `0.00025`

E12 came close to but did not improve the locked Relation selection score, so E10 remains the selected Relation checkpoint and patience advanced from `1/9` to `2/9`; no learning-rate reduction occurred. The runner completed only E12 and stopped at the external-backup boundary before E13. Both 21-file Relation E12 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E10 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E13 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E13

Relation E13 completed from the verified E12 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.2179`
- macro relation F1: `0.79765430`
- minimum-family F1: `0.69502075` (`OBJECT`)
- `POSS_HEAD` F1: `0.79837893`
- `OBJECT` F1: `0.69502075`
- `PARTICIPLE_HEAD` F1: `0.83062201`
- `CASE_GOVERNOR` F1: `0.86659552`
- UAS: `0.87820110`
- LAS: `0.75757031`
- UPOS: `0.91989397`
- selection score: `0.77358111`
- patience: `3/9`
- learning rate: `0.00025`

E13 did not improve the locked Relation selection score, so E10 remains the selected Relation checkpoint and patience advanced from `2/9` to `3/9`; no learning-rate reduction occurred. The runner completed only E13 and stopped at the external-backup boundary before E14. Both 21-file Relation E13 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E10 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E14 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E14

Relation E14 completed from the verified E13 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.2843`
- macro relation F1: `0.80273130`
- minimum-family F1: `0.70631473` (`OBJECT`)
- `POSS_HEAD` F1: `0.80307397`
- `OBJECT` F1: `0.70631473`
- `PARTICIPLE_HEAD` F1: `0.82600000`
- `CASE_GOVERNOR` F1: `0.87553648`
- UAS: `0.87972864`
- LAS: `0.76354569`
- UPOS: `0.92119687`
- selection score: `0.78011562`
- patience: `4/9`
- learning rate: `0.000125`

E14 did not improve the locked Relation selection score, so E10 remains the selected Relation checkpoint and patience advanced from `3/9` to `4/9`. The precommitted four-bad-epoch plateau rule fired exactly once, reducing the learning rate from `0.00025` to `0.000125`. The runner completed only E14 and stopped at the external-backup boundary before E15. Both 21-file Relation E14 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E10 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E15 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E15

Relation E15 completed from the verified E14 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1358`
- macro relation F1: `0.80992595`
- minimum-family F1: `0.71303126` (`OBJECT`)
- `POSS_HEAD` F1: `0.80708661`
- `OBJECT` F1: `0.71303126`
- `PARTICIPLE_HEAD` F1: `0.83497053`
- `CASE_GOVERNOR` F1: `0.88461538`
- UAS: `0.88130111`
- LAS: `0.76192830`
- UPOS: `0.92007368`
- selection score: `0.78611456`
- patience: `0/9`
- learning rate: `0.000125`

E15 improved the locked Relation selection score and became the selected Relation checkpoint, resetting patience from `4/9` to `0/9`; no learning-rate reduction occurred. The runner completed only E15 and stopped at the external-backup boundary before E16. Both 21-file Relation E15 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E15 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E16 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E16

Relation E16 completed from the verified E15 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1132`
- macro relation F1: `0.80404581`
- minimum-family F1: `0.72271678` (`OBJECT`)
- `POSS_HEAD` F1: `0.79277365`
- `OBJECT` F1: `0.72271678`
- `PARTICIPLE_HEAD` F1: `0.83187561`
- `CASE_GOVERNOR` F1: `0.86881720`
- UAS: `0.88152574`
- LAS: `0.76246743`
- UPOS: `0.92187079`
- selection score: `0.78537488`
- patience: `1/9`
- learning rate: `0.000125`

E16 improved the minimum-family/OBJECT F1 but did not improve the locked composite Relation selection score, so E15 remains the selected Relation checkpoint and patience advanced from `0/9` to `1/9`; no learning-rate reduction occurred. The runner completed only E16 and stopped at the external-backup boundary before E17. Both 21-file Relation E16 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E15 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E17 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E17

Relation E17 completed from the verified E16 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1072`
- macro relation F1: `0.80464551`
- minimum-family F1: `0.71753137` (`OBJECT`)
- `POSS_HEAD` F1: `0.80434783`
- `OBJECT` F1: `0.71753137`
- `PARTICIPLE_HEAD` F1: `0.82250242`
- `CASE_GOVERNOR` F1: `0.87420043`
- UAS: `0.88219966`
- LAS: `0.76412975`
- UPOS: `0.92245485`
- selection score: `0.78449292`
- patience: `2/9`
- learning rate: `0.000125`

E17 did not improve the locked Relation selection score, so E15 remains the selected Relation checkpoint and patience advanced from `1/9` to `2/9`; no learning-rate reduction occurred. The runner completed only E17 and stopped at the external-backup boundary before E18. Both 21-file Relation E17 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E15 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E18 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E18

Relation E18 completed from the verified E17 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1064`
- macro relation F1: `0.80636026`
- minimum-family F1: `0.71231957` (`OBJECT`)
- `POSS_HEAD` F1: `0.79885057`
- `OBJECT` F1: `0.71231957`
- `PARTICIPLE_HEAD` F1: `0.83845391`
- `CASE_GOVERNOR` F1: `0.87581699`
- UAS: `0.88184024`
- LAS: `0.76219786`
- UPOS: `0.92169108`
- selection score: `0.78391631`
- patience: `3/9`
- learning rate: `0.000125`

E18 did not improve the locked Relation selection score, so E15 remains the selected Relation checkpoint and patience advanced from `2/9` to `3/9`; no learning-rate reduction occurred. The runner completed only E18 and stopped at the external-backup boundary before E19. Both 21-file Relation E18 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E15 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E19 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E19

Relation E19 completed from the verified E18 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.1009`
- macro relation F1: `0.81147293`
- minimum-family F1: `0.71269788` (`OBJECT`)
- `POSS_HEAD` F1: `0.81608040`
- `OBJECT` F1: `0.71269788`
- `PARTICIPLE_HEAD` F1: `0.84015595`
- `CASE_GOVERNOR` F1: `0.87695749`
- UAS: `0.88381705`
- LAS: `0.76179351`
- UPOS: `0.91989397`
- selection score: `0.78711364`
- patience: `0/9`
- learning rate: `0.000125`

E19 improved the locked Relation selection score, replaced E15 as the selected Relation checkpoint, and reset patience from `3/9` to `0/9`; no learning-rate reduction occurred. The runner completed only E19 and stopped at the external-backup boundary before E20. Both 21-file Relation E19 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E19 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E20 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E20

Relation E20 completed from the verified E19 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.0955`
- macro relation F1: `0.80740423`
- minimum-family F1: `0.70444811` (`OBJECT`)
- `POSS_HEAD` F1: `0.80597015`
- `OBJECT` F1: `0.70444811`
- `PARTICIPLE_HEAD` F1: `0.83902439`
- `CASE_GOVERNOR` F1: `0.88017429`
- UAS: `0.88458082`
- LAS: `0.76516309`
- UPOS: `0.92173601`
- selection score: `0.78282333`
- patience: `1/9`
- learning rate: `0.000125`

E20 did not improve the locked Relation selection score, so E19 remains selected and patience advanced from `0/9` to `1/9`; no learning-rate reduction occurred. The runner completed only E20 and stopped at the external-backup boundary before E21. Both 21-file Relation E20 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E19 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E21 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E21

Relation E21 completed from the verified E20 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.0923`
- macro relation F1: `0.80787185`
- minimum-family F1: `0.71040109` (`OBJECT`)
- `POSS_HEAD` F1: `0.81517510`
- `OBJECT` F1: `0.71040109`
- `PARTICIPLE_HEAD` F1: `0.83037475`
- `CASE_GOVERNOR` F1: `0.87553648`
- UAS: `0.88201995`
- LAS: `0.76403990`
- UPOS: `0.92178093`
- selection score: `0.78441836`
- patience: `2/9`
- learning rate: `0.000125`

E21 did not improve the locked Relation selection score, so E19 remains selected and patience advanced from `1/9` to `2/9`; no learning-rate reduction occurred. The runner completed only E21 and stopped at the external-backup boundary before E22. Both 21-file Relation E21 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E19 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E22 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E22

Relation E22 completed from the verified E21 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.0848`
- macro relation F1: `0.81399062`
- minimum-family F1: `0.71447903` (`OBJECT`)
- `POSS_HEAD` F1: `0.82181110`
- `OBJECT` F1: `0.71447903`
- `PARTICIPLE_HEAD` F1: `0.83877349`
- `CASE_GOVERNOR` F1: `0.88089888`
- UAS: `0.88395184`
- LAS: `0.76390511`
- UPOS: `0.92214035`
- selection score: `0.78921340`
- patience: `0/9`
- learning rate: `0.000125`

E22 improved the locked Relation selection score, replaced E19 as the selected Relation checkpoint, and reset patience from `2/9` to `0/9`; no learning-rate reduction occurred. The runner completed only E22 and stopped at the external-backup boundary before E23. Both 21-file Relation E22 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E22 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E23 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E23

Relation E23 completed from the verified E22 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.0903`
- macro relation F1: `0.81030089`
- minimum-family F1: `0.72080537` (`OBJECT`)
- `POSS_HEAD` F1: `0.81039461`
- `OBJECT` F1: `0.72080537`
- `PARTICIPLE_HEAD` F1: `0.82955665`
- `CASE_GOVERNOR` F1: `0.88044693`
- UAS: `0.88426633`
- LAS: `0.76633121`
- UPOS: `0.92196064`
- selection score: `0.78897646`
- patience: `1/9`
- learning rate: `0.000125`

E23 did not improve the locked Relation selection score, so E22 remains selected and patience advanced from `0/9` to `1/9`; no learning-rate reduction occurred. The runner completed only E23 and stopped at the external-backup boundary before E24. Both 21-file Relation E23 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E22 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E24 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E24

Relation E24 completed from the verified E23 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.0897`
- macro relation F1: `0.80851975`
- minimum-family F1: `0.71448864` (`OBJECT`)
- `POSS_HEAD` F1: `0.80654475`
- `OBJECT` F1: `0.71448864`
- `PARTICIPLE_HEAD` F1: `0.82826300`
- `CASE_GOVERNOR` F1: `0.88478261`
- UAS: `0.88332285`
- LAS: `0.76165873`
- UPOS: `0.92079252`
- selection score: `0.78583533`
- patience: `2/9`
- learning rate: `0.000125`

E24 did not improve the locked Relation selection score, so E22 remains selected and patience advanced from `1/9` to `2/9`; no learning-rate reduction occurred. The runner completed only E24 and stopped at the external-backup boundary before E25. Both 21-file Relation E24 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E22 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E25 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E25

Relation E25 completed from the verified E24 boundary under the unchanged one-epoch protocol:

- combined TRAIN loss: `0.0816`
- macro relation F1: `0.80899506`
- minimum-family F1: `0.71352075` (`OBJECT`)
- `POSS_HEAD` F1: `0.81415929`
- `OBJECT` F1: `0.71352075`
- `PARTICIPLE_HEAD` F1: `0.82646213`
- `CASE_GOVERNOR` F1: `0.88183807`
- UAS: `0.88107647`
- LAS: `0.76022104`
- UPOS: `0.92101716`
- selection score: `0.78556933`
- patience: `3/9`
- learning rate: `0.000125`

E25 did not improve the locked Relation selection score, so E22 remains selected and patience advanced from `2/9` to `3/9`; no learning-rate reduction occurred. The runner completed only E25 and stopped at the external-backup boundary before E26. Both 21-file Relation E25 archives were independently re-materialized; every checksum passed, each reconstructed Relation state matched the canonical source, and both the selected E22 Relation checkpoint and required Syntax E24 parent checkpoint matched their source bytes. Relation E26 and Hard-Negative were not started at this boundary. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E26

Relation E26 completed from the verified E25 state:

- TRAIN loss: `0.0810`
- CALIB macro F1: `0.80558520`
- minimum-family/OBJECT F1: `0.71202749`
- POSS_HEAD F1: `0.80800000`
- OBJECT F1: `0.71202749`
- PARTICIPLE_HEAD F1: `0.82125604`
- CASE_GOVERNOR F1: `0.88105727`
- UAS: `0.88296343`
- LAS: `0.76457903`
- UPOS: `0.92326355`
- selection score: `0.78364444`
- patience: `4/9`
- learning rate: `0.0000625`

E26 did not improve the locked Relation score, so E22 remains the selected Relation checkpoint. Patience advanced from `3/9` to `4/9`, and the deterministic plateau rule reduced the learning rate from `0.000125` to `0.0000625`. Active and durable state/checkpoint mirrors match byte-for-byte, while the frozen Syntax E24 parent remains unchanged. Both 21-file E26 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. Relation E27 and Hard-Negative have not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E27

Relation E27 completed from the verified E26 state under the reduced learning rate:

- TRAIN loss: `0.0728`
- CALIB macro F1: `0.80953949`
- minimum-family/OBJECT F1: `0.71280992`
- POSS_HEAD F1: `0.80769231`
- OBJECT F1: `0.71280992`
- PARTICIPLE_HEAD F1: `0.83222749`
- CASE_GOVERNOR F1: `0.88542825`
- UAS: `0.88552431`
- LAS: `0.76713990`
- UPOS: `0.92218528`
- selection score: `0.78653332`
- patience: `5/9`
- learning rate: `0.0000625`

E27 did not improve the locked Relation score, so E22 remains the selected Relation checkpoint. Patience advanced from `4/9` to `5/9`, and the reduced learning rate remained `0.0000625`. Active and durable state/checkpoint mirrors match byte-for-byte, while the frozen Syntax E24 parent remains unchanged. Both 21-file E27 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. Relation E28 and Hard-Negative have not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E28

Relation E28 completed from the verified E27 state under the reduced learning rate:

- TRAIN loss: `0.0715`
- CALIB macro F1: `0.80953263`
- minimum-family/OBJECT F1: `0.71961326`
- POSS_HEAD F1: `0.80475719`
- OBJECT F1: `0.71961326`
- PARTICIPLE_HEAD F1: `0.83286119`
- CASE_GOVERNOR F1: `0.88089888`
- UAS: `0.88260401`
- LAS: `0.76368047`
- UPOS: `0.92178093`
- selection score: `0.78789046`
- patience: `6/9`
- learning rate: `0.0000625`

E28 did not improve the locked Relation score, so E22 remains the selected Relation checkpoint. Patience advanced from `5/9` to `6/9`, and the learning rate remained `0.0000625`. Active and durable state/checkpoint mirrors match byte-for-byte, while the frozen Syntax E24 parent remains unchanged. Both 21-file E28 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. Relation E29 and Hard-Negative have not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E29

Relation E29 completed from the verified E28 state under the reduced learning rate:

- TRAIN loss: `0.0712`
- CALIB macro F1: `0.81027605`
- minimum-family/OBJECT F1: `0.71491080`
- POSS_HEAD F1: `0.80846774`
- OBJECT F1: `0.71491080`
- PARTICIPLE_HEAD F1: `0.83349191`
- CASE_GOVERNOR F1: `0.88423374`
- UAS: `0.88341271`
- LAS: `0.76305149`
- UPOS: `0.92074760`
- selection score: `0.78707265`
- patience: `7/9`
- learning rate: `0.0000625`

E29 did not improve the locked Relation score, so E22 remains the selected Relation checkpoint. Patience advanced from `6/9` to `7/9`, and the learning rate remained `0.0000625`. Active and durable state/checkpoint mirrors match byte-for-byte, while the frozen Syntax E24 parent remains unchanged. Both 21-file E29 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. Relation E30 and Hard-Negative have not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E30

Relation E30 completed from the verified E29 state under the reduced learning rate:

- TRAIN loss: `0.0658`
- CALIB macro F1: `0.81070934`
- minimum-family/OBJECT F1: `0.71800281`
- POSS_HEAD F1: `0.81182266`
- OBJECT F1: `0.71800281`
- PARTICIPLE_HEAD F1: `0.83479961`
- CASE_GOVERNOR F1: `0.87821229`
- UAS: `0.88408662`
- LAS: `0.76417468`
- UPOS: `0.92249978`
- selection score: `0.78829134`
- patience: `8/9`
- learning rate: `0.0000625`

E30 did not improve the locked Relation score, so E22 remains the selected Relation checkpoint. Patience advanced from `7/9` to `8/9`, and the learning rate remained `0.0000625`. Active and durable state/checkpoint mirrors match byte-for-byte, while the frozen Syntax E24 parent remains unchanged. Both 21-file E30 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. Relation E31 and Hard-Negative have not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Relation E31 closure

Relation E31 completed from the verified E30 state under the reduced learning rate:

- TRAIN loss: `0.1432`
- CALIB macro F1: `0.81202776`
- minimum-family/OBJECT F1: `0.71755188`
- POSS_HEAD F1: `0.81130172`
- OBJECT F1: `0.71755188`
- PARTICIPLE_HEAD F1: `0.83657588`
- CASE_GOVERNOR F1: `0.88268156`
- UAS: `0.88507503`
- LAS: `0.76435439`
- UPOS: `0.92065774`
- selection score: `0.78902592`
- patience: `9/9`
- learning rate: `0.0000625`

E31 did not improve the locked Relation score, so E22 remains the selected Relation checkpoint at `0.78921340`. Patience advanced from `8/9` to `9/9`, closing Relation under the precommitted early-stopping rule. The invocation entered automatic post-Relation cache mining after writing the completion marker; it was interrupted before any Hard-Negative cache, state, metric, checkpoint, or epoch was produced. E32–E34 did not run. Active and durable state/checkpoint/completion-marker mirrors match byte-for-byte, while the frozen Syntax E24 parent remains unchanged. Both 22-file E31 closure archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H01

Hard-Negative H01 completed from the verified Relation E31 closure and its locked E22 Relation checkpoint. The deterministic TRAIN-only mining cache contained 82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples. The epoch used a source hard-negative penalty of `0.100000`:

- TRAIN loss: `0.1655`
- CALIB macro F1: `0.81173907`
- minimum-family/OBJECT F1: `0.71757735`
- POSS_HEAD F1: `0.81636727`
- OBJECT F1: `0.71757735`
- PARTICIPLE_HEAD F1: `0.83772819`
- CASE_GOVERNOR F1: `0.87528345`
- UAS: `0.88246922`
- LAS: `0.76219786`
- UPOS: `0.91975919`
- selection score: `0.78850593`
- patience: `0/9`
- learning rate: `0.00012`

H01 established the initial selected Hard-Negative checkpoint. Active and durable state, cache, and checkpoint mirrors match byte-for-byte; the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H01 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H02 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H02

Hard-Negative H02 completed from the verified H01 boundary with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples). The warm-up source hard-negative penalty was `0.150000`:

- TRAIN loss: `0.1431`
- CALIB macro F1: `0.80191028`
- minimum-family/OBJECT F1: `0.70441080`
- POSS_HEAD F1: `0.79330709`
- OBJECT F1: `0.70441080`
- PARTICIPLE_HEAD F1: `0.83760684`
- CASE_GOVERNOR F1: `0.87231638`
- UAS: `0.88422140`
- LAS: `0.76067032`
- UPOS: `0.91773744`
- selection score: `0.77928351`
- patience: `1/9`
- learning rate: `0.00012`

H02 did not improve the locked Hard-Negative score, so H01 remains selected at `0.78850593`. Patience advanced from `0/9` to `1/9`; the learning rate remained `0.00012`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H02 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H03 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H03

Hard-Negative H03 completed from the verified H02 boundary with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples). The final warm-up source hard-negative penalty was `0.200000`:

- TRAIN loss: `0.1306`
- CALIB macro F1: `0.81389095`
- minimum-family/OBJECT F1: `0.71215207`
- POSS_HEAD F1: `0.81325301`
- OBJECT F1: `0.71215207`
- PARTICIPLE_HEAD F1: `0.84126984`
- CASE_GOVERNOR F1: `0.88888889`
- UAS: `0.88520981`
- LAS: `0.76381526`
- UPOS: `0.92155629`
- selection score: `0.78862166`
- patience: `0/9`
- learning rate: `0.00012`

H03 improved the previous H01 Hard-Negative best of `0.78850593`, so H03 became the selected checkpoint and patience reset from `1/9` to `0/9`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H03 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H04 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H04

Hard-Negative H04 completed from the verified H03 boundary with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples). The full source hard-negative penalty was `0.250000`:

- TRAIN loss: `0.1183`
- CALIB macro F1: `0.80426369`
- minimum-family/OBJECT F1: `0.71520488`
- POSS_HEAD F1: `0.79375000`
- OBJECT F1: `0.71520488`
- PARTICIPLE_HEAD F1: `0.82600382`
- CASE_GOVERNOR F1: `0.88209607`
- UAS: `0.88206488`
- LAS: `0.75936742`
- UPOS: `0.92043310`
- selection score: `0.78329917`
- patience: `1/9`
- learning rate: `0.00012`

H04 did not improve the locked Hard-Negative score, so H03 remains selected at `0.78862166`. Patience advanced from `0/9` to `1/9`; the learning rate remained `0.00012`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H04 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. The canonical boundary is H04 with H05 not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H05

Hard-Negative H05 completed from the verified H04 boundary with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples) and full source hard-negative penalty `0.250000`:

- TRAIN loss: `0.1184`
- CALIB macro F1: `0.80474092`
- minimum-family/OBJECT F1: `0.70646766`
- POSS_HEAD F1: `0.80490296`
- OBJECT F1: `0.70646766`
- PARTICIPLE_HEAD F1: `0.83300199`
- CASE_GOVERNOR F1: `0.87459106`
- UAS: `0.88152574`
- LAS: `0.75999641`
- UPOS: `0.92142151`
- selection score: `0.78121781`
- patience: `2/9`
- learning rate: `0.00012`

H05 did not improve the locked Hard-Negative score, so H03 remains selected at `0.78862166`. Patience advanced from `1/9` to `2/9`; the learning rate remained `0.00012`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H05 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H06 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H06

Hard-Negative H06 completed from the verified H05 boundary with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples) and full source hard-negative penalty `0.250000`:

- TRAIN loss: `0.1143`
- CALIB macro F1: `0.80479915`
- minimum-family/OBJECT F1: `0.70020819`
- POSS_HEAD F1: `0.81362725`
- OBJECT F1: `0.70020819`
- PARTICIPLE_HEAD F1: `0.82224429`
- CASE_GOVERNOR F1: `0.88311688`
- UAS: `0.88175038`
- LAS: `0.76125438`
- UPOS: `0.92038818`
- selection score: `0.77966756`
- patience: `3/9`
- learning rate: `0.00012`

H06 did not improve the locked Hard-Negative score, so H03 remains selected at `0.78862166`. Patience advanced from `2/9` to `3/9`; the learning rate remained `0.00012`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H06 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H07 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H07

Hard-Negative H07 completed from the verified H06 boundary with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples) and full source hard-negative penalty `0.250000`:

- TRAIN loss: `0.1076`
- CALIB macro F1: `0.80235759`
- minimum-family/OBJECT F1: `0.70556309`
- POSS_HEAD F1: `0.79499519`
- OBJECT F1: `0.70556309`
- PARTICIPLE_HEAD F1: `0.82612872`
- CASE_GOVERNOR F1: `0.88274336`
- UAS: `0.88336778`
- LAS: `0.76359062`
- UPOS: `0.92258963`
- selection score: `0.77999020`
- patience: `4/9`
- learning rate: `0.00006`

H07 did not improve the locked Hard-Negative score, so H03 remains selected at `0.78862166`. Patience advanced from `3/9` to `4/9`, triggering the precommitted learning-rate reduction from `0.00012` to `0.00006`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H07 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H08 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H08

Hard-Negative H08 completed from the verified H07 boundary under the reduced learning rate, with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples) and full source hard-negative penalty `0.250000`:

- TRAIN loss: `0.0944`
- CALIB macro F1: `0.80458644`
- minimum-family/OBJECT F1: `0.71488470`
- POSS_HEAD F1: `0.79118573`
- OBJECT F1: `0.71488470`
- PARTICIPLE_HEAD F1: `0.83076923`
- CASE_GOVERNOR F1: `0.88150609`
- UAS: `0.88462575`
- LAS: `0.76565729`
- UPOS: `0.92043310`
- selection score: `0.78404507`
- patience: `5/9`
- learning rate: `0.00006`

H08 did not improve the locked Hard-Negative score, so H03 remains selected at `0.78862166`. Patience advanced from `4/9` to `5/9`; the learning rate remained `0.00006`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H08 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. H09 has not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.

## Hard-Negative H09

Hard-Negative H09 completed from the verified H08 boundary under the reduced learning rate, with the unchanged deterministic TRAIN-only cache (82 CASE_GOVERNOR, 432 OBJECT, 290 PARTICIPLE_HEAD, and 426 POSS_HEAD examples) and full source hard-negative penalty `0.250000`:

- TRAIN loss: `0.0814`
- CALIB macro F1: `0.81167239`
- minimum-family/OBJECT F1: `0.71643836`
- POSS_HEAD F1: `0.80478088`
- OBJECT F1: `0.71643836`
- PARTICIPLE_HEAD F1: `0.84007707`
- CASE_GOVERNOR F1: `0.88539326`
- UAS: `0.88408662`
- LAS: `0.76565729`
- UPOS: `0.92160122`
- selection score: `0.78853128`
- patience: `6/9`
- learning rate: `0.00006`

H09 remained approximately `0.00009038` below the locked H03 Hard-Negative score of `0.78862166`, so H03 remains selected. Patience advanced from `5/9` to `6/9`; the learning rate remained `0.00006`. Active and durable state, cache, and checkpoint mirrors match byte-for-byte, while the locked Relation E22 and Syntax E24 parents remain unchanged. Both 24-file H09 archives were independently re-materialized, checksum-verified, state-reconstructed, and byte-compared. The canonical boundary is H09 with H10 not started. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened.


## Hard-Negative overfit guard amendment before H10

Before any H10 optimizer step, a non-retroactive Hard-Negative overfit guard was added in response to the H03-H09 selection plateau. Its counter starts at `0/3`; H04-H09 are not backfilled. H10 records the first comparable combined TRAIN loss and gold-CALIB objective loss and cannot increment the counter. From H11 onward, a signal requires all three conditions in the same epoch: the locked selection score does not improve, combined TRAIN loss falls, and the combined gold-CALIB objective loss rises by at least 0.1% relative to the preceding guarded epoch. The counter increments only on consecutive signals and otherwise resets to zero. At `3/3`, the selected best Hard-Negative checkpoint is frozen and the stage closes before any later epoch.

The existing `9/9` patience and deterministic learning-rate rules remain authoritative and can close the stage earlier. CALIB is used only for the same gold objective and locked selection measurements; the deterministic TRAIN-only hard-negative cache is not applied to CALIB. `INTERNAL_VAL`, external holdouts, and official TEST remain unopened. H09 remains the canonical boundary and H10 has not started at the time of this amendment.
