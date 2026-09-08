"""Selection policy edge cases; no corpus, training or workspace writes."""
import unittest
from .calibrate import choose


def row(correct=True, feature=True, lm=0, fm=0, eligible=True):
    return dict(A2_eligible=eligible, lemma_margin=lm, feature_margin=fm,
                preferred_lemma_pos=correct, preferred_declared_features=feature, aligned=True)


class SelectionTests(unittest.TestCase):
    def test_no_feasible_pair_is_not_falsely_promoted(self):
        _, best = choose([row(False, False)], [0, 1], 92)
        self.assertIsNone(best)

    def test_both_precisions_required(self):
        _, best = choose([row(True, False)], [0], 92)
        self.assertIsNone(best)

    def test_maximum_coverage_with_boundary_included(self):
        rows = [row(lm=1, fm=1) for _ in range(12)] + [row(False, False, lm=0, fm=0)]
        _, best = choose(rows, [0, 1, 2], 92)
        self.assertEqual(best['accepted'], 13)  # 12/13 exceeds 92%; do not prefer 100% at lower coverage.
        self.assertEqual(best['thresholds'], {'lemma_threshold': 0, 'feature_threshold': 0})

    def test_margin_gate_rejects_low_score_errors(self):
        rows = [row(lm=1, fm=1)] * 10 + [row(False, False, lm=0, fm=0)] * 2
        _, best = choose(rows, [0, 1], 92)
        self.assertEqual(best['accepted'], 10)
        self.assertEqual(best['thresholds'], {'lemma_threshold': 0, 'feature_threshold': 1})

    def test_single_group_does_not_bypass_eligibility(self):
        _, best = choose([row(lm=None, fm=None), row(False, False, lm=None, fm=None, eligible=False)], [20], 92)
        self.assertEqual(best['accepted'], 1)
        self.assertEqual(best['accepted_all_word_coverage_pct'], 50)

    def test_nonfinite_margins_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'NONFINITE_MARGIN'):
            choose([row(lm=float('nan'))], [0], 92)


if __name__ == '__main__':
    unittest.main()
