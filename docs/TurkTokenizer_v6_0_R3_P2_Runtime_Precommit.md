# TurkTokenizer v6.0 R3-P2 runtime precommit

R3-P2 remains a paired, single-variable TRAIN/CALIB ablation. This runtime
addendum binds the existing loss precommit to an interruption-safe execution
before either real arm starts.

Both arms restore the same selected R1 Syntax E10 checkpoint and the same
completed Syntax E12 sampler boundary. They use seed 51104, Relation E50,
Hard-Negative E50, patience 9,
the same optimizer and learning rates, and the same deterministic LR reduction
at plateau 4/9. Every qualifying improvement resets patience to 0/9.

The execution order is control followed by candidate. The control retains the
R1 joint focal likelihood; the candidate uses the precommitted zero-margin
hardest-competitor ranking loss. No other model, data, inference, threshold,
hard-negative, or CASE_GOVERNOR behavior changes.

Arm metrics remain blinded until both arms close. The matched exact-edge gate
is fixed as micro head-top1 over gold-positive sources pooled across
POSS_HEAD, OBJECT, and PARTICIPLE_HEAD. Every previously published CALIB gate
remains required.

Each epoch ends at an atomic resumable boundary with a verified local mirror.
Two independent persistent checkpoint packages and a public-safe GitHub status
commit must be verified before the next epoch starts.

The runtime smoke passed without unpickling TRAIN or CALIB. INTERNAL_VAL,
official TEST, and external holdouts remain unopened.

The frozen data audit is checked through its locked metadata, while payload
hashing is restricted to the TRAIN/CALIB inputs actually required by this
screen. Recorded-only INTERNAL_VAL and historical split-map entries are never
resolved or opened by the runtime.
