# R5 AB00-R1-S02 v0.1.0 development snapshot

S02 repairs lossless orthographic spans, preserves adjectival interpretations of
possessive participles, and prevents noun phrases from crossing gaps left by
clause punctuation or coordination. It retains the S01-CP1 context weights as
the default. This is an experimental development snapshot, not a flawless
semantic analyzer or a promotion of the separate v6/R4 line.

| Main diagnostic (3,000 contextual words) | S01-CP1 | S02 |
|---|---:|---:|
| Exact token span | 2,983 | 3,000 |
| Gold lemma and POS available among candidates | 2,734 | 2,767 |
| Preferred lemma and POS correct | 2,509 | 2,528 |
| Correct committed decision | 2,390 | 2,406 |
| Incorrect committed decision | 350 | 337 |
| Abstention or missing output | 260 | 257 |

The paired preference comparison fixes 21 former errors and introduces two,
for a net gain of 19. Of the 225 S01-CP1 errors where the correct candidate
already existed, three are fixed and 222 remain. S02 has 239 errors with a
correct candidate present and 233 with that candidate absent. These diagnostics
are development evidence; they do not establish fresh-test generalization.

S02 passes 31 of 32 comparisons against CP1. The failed comparison is the
reserve set's correct committed count (888 to 887). Reserve preferred-correct
count rises from 932 to 933 and incorrect commitments fall from 249 to 247.
The local B0 comparison passes 29 of 32 gates; inherited paired, probe-selection,
and probe-error limitations remain. This is not an all-gates-passed claim.

Training-only residual scoring was explored but rejected as the default:
main preference accuracy falls to 2,480 correct. An exploratory equal blend
with CP1 reaches 2,525 correct preferences and 314 incorrect commitments, with
more abstentions and only 25 of 32 CP1 comparisons passing. The blend remains
an explicit optional experiment. No evaluation labels were used for gradients;
the exploratory blend is not a preregistered confirmatory result.

Validation includes deterministic segmentation and Unicode reconstruction,
number-suffix harmony positive/negative cases, retained morphology candidates,
possessive-participle branches, phrase boundaries, main/paired/probe/reserve
comparisons, and a fresh-package CLI smoke run. The candidate audit found no
removed or mutated parent candidates. All package members were checksum checked.

The implementation overlay is in `src/r5_s02/`. Copy its Python modules to the
root of an authorized S01-CP1/S02 research package to run it. The morphology
registry, lexicon, parent runtime, and model files must be supplied by that
package. The overlay is intentionally not a standalone installation; the
standalone segmentation and numeral helpers can be imported directly.

The full reproducible package and detailed diagnostics were verified in two
local backup locations. ChatGPT Library upload is pending because the Library
reports that storage is full. No successful Library receipt is claimed.
Corpora, model weights, split inventories and private per-record audits remain
outside this public commit under `PUBLICATION_POLICY.md`.

Next work: decompose existing-candidate failures into local score preference,
joint sentence overrides, lexical representation mismatch and ambiguity.
Keep the S02 baseline fixed; report new regressions alongside corrections.
