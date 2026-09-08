import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ['OPENBLAS_NUM_THREADS'] = '1'
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / '.deps-s06'), str(ROOT / '.deps-s05six')]
import numpy as np
from .numerics import loss, train_epoch
from .train import install_a1, publication_acknowledged, checkpoint
from s05_ua_features import UARanker
from training_controls.e70p9.epoch_control import digest, atomic_json


class A3EpochTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(42)
        self.X = self.rng.normal(size=(17, 5))
        self.b = self.rng.normal(size=17)
        self.config = {'learning_rate': 0.001, 'batch_size': 4, 'beta1': 0.9, 'beta2': 0.999, 'epsilon': 1e-8}

    def test_ranking_gradient_matches_finite_difference(self):
        theta = np.array([0.8, 1.1, 0.9, 1.2, 0.7])
        analytic = loss(theta, self.X, self.b, 0.1)[1]
        for j in range(5):
            d = np.zeros(5); d[j] = 1e-6
            numeric = (loss(theta + d, self.X, self.b, 0.1)[0] - loss(theta - d, self.X, self.b, 0.1)[0]) / 2e-6
            self.assertAlmostEqual(analytic[j], numeric, places=7)

    def test_diagnostic_loss_does_not_include_regularizer(self):
        theta = np.arange(5) / 5 + 0.5
        expected = np.maximum(0, 1 - self.b - self.X @ theta) ** 2
        self.assertAlmostEqual(loss(theta, self.X, self.b)[0], np.mean(expected), places=12)

    def test_full_pass_and_checkpoint_resume_are_identical(self):
        theta = np.ones(5); m = np.zeros(5); v = np.zeros(5)
        step, seen = train_epoch(theta, m, v, 0, self.X, self.b, self.rng, self.config, 0.1, [0.05, 3])
        self.assertEqual((step, seen), (5, 17))
        with tempfile.TemporaryDirectory(prefix='a3-optimizer-test-') as name:
            folder = Path(name)
            (folder / 'a1-ranker.json').write_text('{"weights":{}}', encoding='utf-8')
            (folder / 'fixed-probes.npz').write_bytes(b'fixed diagnostic fixture')
            artifacts = checkpoint(folder, folder, theta, m, v, step, self.rng, 1, 'fixed-hash', {})
            train_epoch(theta, m, v, step, self.X, self.b, self.rng, self.config, 0.1, [0.05, 3])
            with np.load(artifacts['trainer_state'], allow_pickle=False) as z:
                metadata = json.loads(str(z['metadata']))
                self.assertEqual((metadata['epoch'], metadata['freeze_sha256']), (1, 'fixed-hash'))
                restored = [z[n].copy() for n in ('theta', 'adam_m', 'adam_v')]
                rng = np.random.default_rng(); rng.bit_generator.state = metadata['rng']
                train_epoch(*restored, int(z['step']), self.X, self.b, rng, self.config, 0.1, [0.05, 3])
            for a, b in zip((theta, m, v), restored):
                np.testing.assert_array_equal(a, b)

    def test_channel_bounds_hold_under_large_update(self):
        theta = np.ones(5); m = np.zeros(5); v = np.zeros(5)
        config = {**self.config, 'learning_rate': 100}
        train_epoch(theta, m, v, 0, self.X, self.b, self.rng, config, 0.1, [0.05, 3])
        self.assertTrue(np.all(theta >= 0.05) and np.all(theta <= 3))

    def test_install_preserves_A3_scale_in_both_UA_selectors(self):
        child = SimpleNamespace(ranker=UARanker.__new__(UARanker))
        legacy = SimpleNamespace()
        selector = SimpleNamespace(ranker=UARanker.__new__(UARanker), reference_ua=child,
                                   reference_selector=legacy, a123_models={})
        rt = SimpleNamespace(weights=(0.73, 1, 1, 1, 1), context_selector=selector)
        model = {'version': 'fixture', 'weights': {}}
        install_a1(rt, model, 'fixture-hash')
        self.assertEqual(selector.ranker.scale, 0.73)
        self.assertEqual(child.ranker.scale, 0.73)
        self.assertIs(selector.ranker.model, model)
        self.assertFalse(hasattr(legacy, 'ranker'))

    def test_publication_gate_requires_verified_matching_epoch_files(self):
        with tempfile.TemporaryDirectory(prefix='a3-publication-test-') as name:
            folder = Path(name)
            for n in ('state.json', 'metrics.jsonl', 'training.log', 'checkpoint-sha256.json'):
                (folder / n).write_text('fixture', encoding='utf-8')
            hashes = {p.name: digest(p) for p in folder.iterdir()}
            atomic_json(folder / 'ready.json', {'epoch': 1, 'files': hashes, 'cli_synced': False})
            self.assertFalse(publication_acknowledged(folder))
            ack = {'epoch': 1, 'files': hashes, 'repository': 'ozelturktarkan/TurkTokenizer', 'verified': True, 'commit': 'a' * 40}
            atomic_json(folder / 'published.json', {**ack, 'epoch': 2})
            self.assertFalse(publication_acknowledged(folder))
            atomic_json(folder / 'published.json', {**ack, 'verified': False})
            self.assertFalse(publication_acknowledged(folder))
            atomic_json(folder / 'published.json', ack)
            self.assertTrue(publication_acknowledged(folder))
            (folder / 'training.log').write_text('changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'OUTBOX_CHANGED'):
                publication_acknowledged(folder)


if __name__ == '__main__':
    unittest.main()
