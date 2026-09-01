# TurkTokenizer v6.0 R2-P10 precommit

R2-P10 is a frozen-checkpoint, CALIB-only decision-coupling screen. It does not train or update model parameters.

The A1–R1–H21 error decomposition shows that H21 improves OBJECT source F1 and head top-1 accuracy when considered separately, while the final exact-edge F1 remains below A1. The only changed variable is therefore the direct-relation activation score:

- Parent: source probability × maximum head probability.
- Candidate: source probability.
- Head choice: unchanged argmax head.
- CASE_GOVERNOR: unchanged parent score and threshold.
- Threshold grid: 0.05–0.95 in 0.01 steps with the existing F1/recall/0.5-proximity tie-break.

Promotion requires all of the following on CALIB:

- OBJECT F1 ≥ 0.719407.
- Macro relation F1 ≥ 0.810756.
- Minimum-family F1 ≥ 0.719407.
- POSS_HEAD and PARTICIPLE_HEAD remain within 0.002 of the parent H21 result.
- CASE_GOVERNOR policy remains unchanged.

INTERNAL_VAL, TEST, and external holdouts remain unopened. Public artifacts contain aggregate metrics and protocol documentation only.
