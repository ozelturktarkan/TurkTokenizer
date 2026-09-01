# TurkTokenizer v6.0 R3-P2 precommit

R3-P2 is a paired, single-variable TRAIN/CALIB ablation. It follows the closed R3-P1 decision-rescue line and tests whether an explicitly ranking-oriented training loss improves exact source–head ordering.

The control and candidate start from the same selected R1 syntax boundary and use the same seed, model, data, optimizer settings, stage ceilings, patience, checkpoint selection, threshold grid, and hard-negative protocol. The only difference is the loss for `POSS_HEAD`, `OBJECT`, and `PARTICIPLE_HEAD`:

- Control: the existing R1 balanced joint focal likelihood over `NULL ∪ valid heads`.
- Candidate: zero-margin logistic ranking of the target class against the strongest valid competitor.

For a positive source, the consensus-preferred head must outrank both `NULL` and every wrong head. For an absent source, `NULL` must outrank every head. `CASE_GOVERNOR` and the inference rule remain unchanged. No margin, temperature, or auxiliary-loss weight will be tuned.

Promotion requires all precommitted CALIB gates, including improvement over the matched control on OBJECT F1 and exact direct-edge ordering, no material family or syntax regression, and the existing aggregate quality floors. A failed gate closes the line without post-hoc rescue.

`INTERNAL_VAL`, official TEST, and external holdouts remain sealed. Public artifacts contain protocol and aggregate status only; no dataset, checkpoint, private hash, sealed metadata, or split inventory is published.
