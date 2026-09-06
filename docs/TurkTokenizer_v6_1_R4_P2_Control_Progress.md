# TurkTokenizer v6.1 R4-P2 matched focal control progress

> Status: ACTIVE — Relation E20 completed and independently archived; E21 pending.

## Purpose

This arm is the matched focal control for R4-P2. It starts Relation training fresh from the independently verified R4-P1 Syntax E24 parent and changes no learning mechanism relative to R4-P1. Its purpose is to establish the paired baseline against which the fixed R4-P0 adapter-plus-PCGrad candidate can later be judged.

## Locked control

- Seed: `51104`; batch size: `24`.
- Syntax parent: R4-P1 selected Syntax E24; relation sampler begins at the completed Syntax boundary, epoch `27`.
- Relation and Hard-Negative parameters are initialized fresh.
- The R4-P1 focal trainer and objective are reused unchanged.
- Family adapters: disabled.
- PCGrad: disabled.
- Ranking loss: disabled and reserved for R4-P3.
- Relation ceiling: E50; patience: `9`; initial learning rate: `0.00025`.
- Hard-Negative ceiling: H50; patience: `9`; initial learning rate: `0.00012`.
- A deterministic learning-rate halving applies at the fourth consecutive non-improving epoch.
- Hard-Negative penalty warmup is `0.10`, `0.15`, `0.20`, then `0.25`.
- Relation and Hard-Negative each use a symmetric `0/3` overfitting guard from their first epoch. A signal requires no selection improvement, falling TRAIN loss, and at least a 0.1% rise in gold-CALIB objective loss; three consecutive signals stop the stage safely.
- Final CALIB screening, if reached, will be executed twice unchanged and must agree exactly.
- Every completed epoch boundary must be retained in two independent private packages and re-read with all manifest checksums verified before the next epoch begins.

## Start-gate result

The precommit, architecture smoke test, and zero-step start gate passed. The verified start package contains 16 files, with all 15 manifest checksums passing in each of two independently re-materialized copies. The selected R4-P1 Syntax E24 parent, sampler boundary, fresh Relation/Hard-Negative state, and zero optimizer-step condition were all confirmed.

## Relation progress

| Epoch | TRAIN loss | Gold-CALIB objective loss | Macro F1 | Min/OBJECT F1 | UAS | LAS | Selection score | Patience | LR | Overfit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E01 | 0.5198 | 1.847522 | 0.791514 | 0.683742 | 0.874382 | 0.751460 | 0.766242 | 0/9 | 0.00025 | 0/3 baseline |
| E02 | 0.4175 | 1.615396 | 0.795592 | 0.704782 | 0.873034 | 0.754920 | 0.774421 | 0/9 | 0.00025 | 0/3 |
| E03 | 0.3943 | 1.664362 | 0.795990 | 0.706499 | 0.877527 | 0.759367 | 0.775787 | 0/9 | 0.00025 | 0/3 |
| E04 | 0.3192 | 1.779728 | 0.791875 | 0.698649 | 0.876359 | 0.754021 | 0.770813 | 1/9 | 0.00025 | 1/3 |
| E05 | 0.2755 | 1.821188 | 0.806698 | 0.715609 | 0.876718 | 0.755054 | 0.784091 | 0/9 | 0.00025 | 0/3 |
| E06 | 0.2412 | 2.003071 | 0.800187 | 0.718874 | 0.875595 | 0.754830 | 0.781090 | 1/9 | 0.00025 | 1/3 |
| E07 | 0.2361 | 1.989568 | 0.797455 | 0.714586 | 0.877887 | 0.758020 | 0.778754 | 2/9 | 0.00025 | 0/3 |
| E08 | 0.2028 | 2.304503 | 0.802046 | 0.702722 | 0.877123 | 0.756807 | 0.778068 | 3/9 | 0.00025 | 1/3 |
| E09 | 0.2116 | 1.858740 | 0.791408 | 0.706729 | 0.873933 | 0.756807 | 0.772725 | 4/9 | 0.000125 | 0/3 |
| E10 | 0.1613 | 2.321066 | 0.809643 | 0.726141 | 0.880807 | 0.764040 | 0.789598 | 0/9 | 0.000125 | 0/3 |
| E11 | 0.1404 | 2.322751 | 0.809290 | 0.718559 | 0.880313 | 0.760086 | 0.787030 | 1/9 | 0.000125 | 0/3 |
| E12 | 0.1215 | 2.577956 | 0.810655 | 0.720955 | 0.880852 | 0.764130 | 0.788795 | 2/9 | 0.000125 | 1/3 |
| E13 | 0.1186 | 2.338338 | 0.805493 | 0.709677 | 0.879684 | 0.759951 | 0.782370 | 3/9 | 0.000125 | 0/3 |
| E14 | 0.1050 | 2.717765 | 0.805319 | 0.706627 | 0.879863 | 0.762962 | 0.781671 | 4/9 | 0.0000625 | 1/3 |
| E15 | 0.0993 | 2.567901 | 0.807714 | 0.707733 | 0.882155 | 0.761165 | 0.783416 | 5/9 | 0.0000625 | 0/3 |
| E16 | 0.0964 | 2.532316 | 0.813825 | 0.720721 | 0.883098 | 0.764669 | 0.790788 | 0/9 | 0.0000625 | 0/3 |
| E17 | 0.0926 | 2.457386 | 0.811019 | 0.714758 | 0.881571 | 0.763815 | 0.787368 | 1/9 | 0.0000625 | 0/3 |
| E18 | 0.0937 | 2.714155 | 0.806851 | 0.712017 | 0.880987 | 0.762333 | 0.784060 | 2/9 | 0.0000625 | 0/3 |
| E19 | 0.0786 | 3.024713 | 0.807794 | 0.712991 | 0.882334 | 0.763096 | 0.785032 | 3/9 | 0.0000625 | 1/3 |
| E20 | 0.0795 | 2.910387 | 0.809789 | 0.709254 | 0.879998 | 0.760176 | 0.784789 | 4/9 | 0.00003125 | 0/3 |

E01 was independently re-evaluated from its persisted state. Both 28-file private A/B packages were re-materialized; all 27 manifest checksums, source/A/B byte equality, the selected checkpoint, and reconstructed state passed. This freshly executed arm—not the historical P1 trajectory—is the locked paired control that the R4-P2 adapter-plus-PCGrad candidate must beat.

E02 improved the selected control checkpoint; TRAIN and gold-CALIB objective losses both fell, so the overfit signal remained false at `0/3`. Its two 28-file private packages passed all 27 manifest checksums, source/A/B byte equality, checkpoint, and reconstructed-state checks.

E03 improved the selected score. TRAIN loss fell and gold-CALIB objective loss rose, but the improvement condition kept the divergence signal false at `0/3`. Its corrected 28-file A/B archives passed all 27 checksums, byte equality, checkpoint, and reconstructed-state checks; one transfer-helper temporary file was removed before acceptance.

E04 did not improve; TRAIN loss fell while gold-CALIB objective loss rose, producing the first divergence signal (`1/3`). Its two 28-file packages passed all 27 checksums, byte equality, selected-checkpoint preservation, and reconstructed-state checks.

E05 established a new selected checkpoint. Although TRAIN loss fell and gold-CALIB objective loss rose, selection improved, so both patience and the divergence streak reset to zero. Its two 28-file packages passed all 27 checksums, byte equality, checkpoint, and reconstructed-state checks.

E06 did not improve; TRAIN loss fell and gold-CALIB objective loss rose, so the divergence streak is `1/3`. E05 remains selected. Both 28-file E06 packages passed all 27 checksums, byte equality, selected-checkpoint preservation, and reconstructed-state checks.

E07 did not improve, but gold-CALIB objective loss fell, breaking the divergence sequence and resetting it to `0/3`. E05 remains selected. Both 28-file E07 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E08 did not improve; TRAIN loss fell and gold-CALIB objective loss rose, starting a new divergence sequence at `1/3`. E05 remains selected. Both 28-file E08 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E09 did not improve; patience reached `4/9` and the precommitted LR reduction changed `0.00025` to `0.000125`. TRAIN loss rose and CALIB objective loss fell, resetting divergence to `0/3`. E05 remains selected. Both 28-file E09 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E10 established a new selected checkpoint after the LR reduction. Selection improved, resetting patience and holding divergence at `0/3`; minimum-family/OBJECT F1 crossed the R4 planning floor, but this remains a control-stage result. Both 28-file E10 packages passed all 27 checksums, byte equality, checkpoint, and reconstructed-state checks.

E11 did not improve. Its CALIB objective rise was below the precommitted 0.1% relative threshold, so divergence remained `0/3`; E10 stays selected. Both 28-file E11 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E12 did not improve; TRAIN loss fell and gold-CALIB objective loss rose, advancing divergence to `1/3`. E10 remains selected. Both 28-file E12 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E13 did not improve, but CALIB objective loss fell and broke the divergence sequence, resetting it to `0/3`. E10 remains selected. Both 28-file E13 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E14 did not improve; the new post-improvement plateau reached `4/9`, so the unchanged P1 schedule halved LR from `0.000125` to `0.0000625`. TRAIN fell and CALIB objective rose, advancing divergence to `1/3`. E10 remains selected. Both 28-file E14 packages passed all 27 checksums, byte equality, checkpoint preservation, and reconstructed-state checks.

E15 did not improve. TRAIN loss fell, but gold-CALIB objective loss also fell, breaking the divergence sequence and resetting it from `1/3` to `0/3`. E10 remains selected; patience is `5/9` and LR remains `0.0000625`. Both 28-file E15 packages passed all 27 checksums, source/A/B byte equality, checkpoint preservation, and reconstructed-state checks.

E16 established a new selected checkpoint at score `0.79078781`, resetting patience from `5/9` to `0/9`. TRAIN and gold-CALIB objective losses both fell, while selection improved, so divergence remained `0/3`; LR remains `0.0000625`. Both 28-file E16 packages passed all 27 checksums, source/A/B byte equality, checkpoint, and reconstructed-state checks.

E17 did not improve; E16 remains selected. TRAIN and gold-CALIB objective losses both fell, so divergence remained `0/3`; patience is `1/9` and LR remains `0.0000625`. Both 28-file E17 packages passed all 27 checksums, source/A/B byte equality, checkpoint preservation, and reconstructed-state checks.

E18 did not improve; E16 remains selected. Gold-CALIB objective loss rose, but TRAIN loss also rose, so the divergence signal remained false at `0/3`; patience is `2/9` and LR remains `0.0000625`. Both 28-file E18 packages passed all 27 checksums, source/A/B byte equality, checkpoint preservation, and reconstructed-state checks.

E19 did not improve; E16 remains selected. TRAIN loss fell while gold-CALIB objective loss rose, producing the first signal of a new divergence sequence (`1/3`); patience is `3/9` and LR remains `0.0000625`. Both 28-file E19 packages passed all 27 checksums, source/A/B byte equality, checkpoint preservation, and reconstructed-state checks.

E20 did not improve; E16 remains selected. The post-improvement plateau reached `4/9`, so the unchanged schedule halved LR from `0.0000625` to `0.00003125`. TRAIN rose and gold-CALIB objective loss fell, breaking the prior divergence sequence and resetting it to `0/3`. Both 28-file E20 packages passed all 27 checksums, source/A/B byte equality, checkpoint preservation, and reconstructed-state checks.

Relation E21 has not started at this public boundary. `INTERNAL_VAL`, external BOUN/IMST/Penn holdouts, and official TEST remain unopened.
