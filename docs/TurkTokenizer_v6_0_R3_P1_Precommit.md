# TurkTokenizer v6.0 R3-P1 precommit

R3-P1 is a frozen-checkpoint, CALIB-only screen built from the closed R1 null-arc model. It does not train or update model parameters.

R1 defines direct-relation source evidence by comparing the log-sum-exp of all non-null head arcs with a learned NULL logit. The current evaluation then multiplies that source probability by maximum head probability, which may count head dispersion twice. R3-P1 changes only the activation score:

- Parent: source probability × maximum head probability.
- Candidate: source probability.
- Head choice: unchanged argmax head.
- CASE_GOVERNOR: unchanged R1 score and threshold.
- Threshold grid: 0.05–0.95 in 0.01 steps with the existing F1/recall/0.5-proximity tie-break.

Promotion requires every CALIB gate:

- OBJECT F1 ≥ 0.719407.
- Macro relation F1 ≥ 0.810756.
- Minimum-family F1 ≥ 0.719407.
- POSS_HEAD and PARTICIPLE_HEAD remain within 0.002 of A1.
- CASE_GOVERNOR policy remains unchanged.

INTERNAL_VAL, TEST, and external holdouts remain unopened. Public artifacts contain aggregate metrics and protocol documentation only.

## Closure

The CALIB screen completed with macro F1 `0.805125`, minimum/OBJECT F1 `0.711779`, unchanged `UAS=0.883053`, and unchanged `LAS=0.764309`. OBJECT decreased by `-0.002004` and macro F1 by `-0.002702` versus R1. The precommitted decision is `DROP_AFTER_SCREEN`. See [the decision note](TurkTokenizer_v6_0_R3_P1_Decision.md).
