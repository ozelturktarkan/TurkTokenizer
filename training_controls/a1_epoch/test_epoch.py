import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ['OPENBLAS_NUM_THREADS'] = '1'
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / '.deps-s06'), str(ROOT / '.deps-s05six')]
import numpy as np
from scipy.sparse import csr_matrix
from .numerics import objective, train_epoch, subset
from training_controls.e70p9.epoch_control import EpochRun, read


class EpochNumericsTests(unittest.TestCase):
    def setUp(self):
        self.data = (csr_matrix([[1., 0.], [0., 1.], [1., 1.], [2., 0.], [0., 2.]]),
                     np.array([0, 3]), np.array([3, 5]), np.array([True, False, True, False, True]),
                     np.array([.2, -.1, .4, .1, -.2]))
        self.config = {'learning_rate': .001, 'batch_size': 1, 'beta1': .9, 'beta2': .999, 'epsilon': 1e-8}

    def test_partial_label_gradient_matches_finite_difference(self):
        w = np.array([.1, -.2]); analytic = objective(w, self.data, .1)[1]
        for i in range(2):
            d = np.zeros(2); d[i] = 1e-6
            numeric = (objective(w + d, self.data, .1)[0] - objective(w - d, self.data, .1)[0]) / 2e-6
            self.assertAlmostEqual(analytic[i], numeric, places=7)

    def test_minibatch_loss_equals_full_data_mean(self):
        w = np.array([.1, -.2])
        parts = [objective(w, subset(self.data, np.array([i])), gradient=False) for i in range(2)]
        self.assertAlmostEqual(np.mean(parts), objective(w, self.data, gradient=False), places=12)

    def test_optimizer_resume_is_identical_to_continuous_training(self):
        w = np.array([.1, -.2]); m = np.zeros(2); v = np.zeros(2); rng = np.random.default_rng(42)
        step, seen = train_epoch(w, m, v, 0, self.data, rng, self.config)
        self.assertEqual((step, seen), (2, 2))
        saved = [x.copy() for x in (w, m, v)]; saved_rng = copy.deepcopy(rng.bit_generator.state)
        train_epoch(w, m, v, step, self.data, rng, self.config)
        resumed_rng = np.random.default_rng(); resumed_rng.bit_generator.state = saved_rng
        train_epoch(*saved, step, self.data, resumed_rng, self.config)
        for expected, actual in zip((w, m, v), saved): np.testing.assert_array_equal(expected, actual)

    def test_seed_baseline_is_retained_and_failure_counts_from_e01(self):
        policy = read(ROOT / 'training_controls/e70p9/protocol.json')
        policy['backup']['minimum_free_bytes_after_write'] = 0
        with tempfile.TemporaryDirectory(prefix='a1-baseline-test-') as name:
            base = Path(name); a = base / 'weights'; a.write_text('baseline')
            b = base / 'trainer'; b.write_text('{}')
            run = EpochRun(base / 'run', 'A1', policy)
            run.seed_baseline(train_loss=1., dev_loss=1., dev_correct=100, dev_total=200,
                              artifacts={'weights': a, 'trainer_state': b})
            a.write_text('epoch 1')
            result = run.complete_epoch(1, train_loss=.9, dev_loss=1.1, dev_correct=99, dev_total=200,
                                        safe=True, artifacts={'weights': a, 'trainer_state': b})
            self.assertEqual((result['best_epoch'], result['patience_count']), (0, 1))
            self.assertEqual(Path(result['best_checkpoint']['weights']).read_text(), 'baseline')
            for epoch in (2, 3, 4):
                run.complete_epoch(epoch, train_loss=.8, dev_loss=.9, dev_correct=100 + epoch,
                                   dev_total=200, safe=True, artifacts={'weights': a, 'trainer_state': b})
            self.assertTrue((run.root / 'copy-a/epoch-000000/weights.checkpoint').exists())


if __name__ == '__main__': unittest.main()
