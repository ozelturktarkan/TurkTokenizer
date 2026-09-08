import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from training_controls.e70p9.epoch_control import EpochRun, advance, digest, read
from training_controls.e70p9.git_journal import GitJournal


POLICY = read(Path(__file__).with_name('protocol.json'))


def step(previous, epoch, correct, **overrides):
    args = dict(train_loss=100 - epoch, dev_loss=1.0, dev_correct=correct,
                dev_total=1000, safe=True, policy=POLICY)
    args.update(overrides)
    return advance(previous, epoch, **args)


class StoppingTests(unittest.TestCase):
    def test_nine_ties_stop_and_new_best_resets(self):
        state = step(None, 1, 100)
        for e in range(2, 10): state = step(state, e, 100)
        self.assertFalse(state['stop'])
        self.assertEqual(state['patience_count'], 8)
        state = step(state, 10, 101)
        self.assertEqual(state['patience_count'], 0)
        for e in range(11, 20): state = step(state, e, 101)
        self.assertEqual(state['stop_reason'], 'PATIENCE_9')
        self.assertEqual(state['best_epoch'], 10)
        with self.assertRaises(ValueError): step(state, 20, 102)

    def test_e70_is_hard_limit(self):
        state = None
        for e in range(1, 71): state = step(state, e, e)
        self.assertEqual(state['stop_reason'], 'MAX_EPOCH_70')
        self.assertEqual(state['best_epoch'], 70)

    def test_overfit_begins_e21_and_stops_e23(self):
        state = None
        for e in range(1, 21): state = step(state, e, 100 + e)
        for e in range(21, 24):
            state = step(state, e, 119, dev_loss=1 + (e - 20) / 10)
            self.assertEqual(state['overfit_count'], e - 20)
            self.assertEqual(state['stop'], e == 23)
        self.assertEqual(state['best_epoch'], 20)
        self.assertEqual(state['stop_reason'], 'OVERFITTING_3')

    def test_signal_resets_and_is_disabled_through_e20(self):
        state = None
        for e in range(1, 19): state = step(state, e, 100 + e)
        state = step(state, 19, 117, dev_loss=1.1)
        state = step(state, 20, 117, dev_loss=1.2)
        self.assertEqual(state['overfit_count'], 0)
        state = step(state, 21, 117, dev_loss=1.3)
        self.assertEqual(state['overfit_count'], 1)
        state = step(state, 22, 117, dev_loss=1.2)
        self.assertEqual(state['overfit_count'], 0)

    def test_unsafe_peak_is_not_selected(self):
        state = step(None, 1, 100)
        state = step(state, 2, 500, safe=False)
        self.assertEqual((state['best_epoch'], state['best_correct'], state['patience_count']), (1, 100, 1))

    def test_invalid_metric_and_sequence_rejected(self):
        state = step(None, 1, 100)
        for kwargs in ({'dev_total': 999}, {'dev_loss': float('nan')}, {'safe': None}):
            with self.assertRaises(ValueError): step(state, 2, 100, **kwargs)
        with self.assertRaises(ValueError): step(state, 3, 100)


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='e70-control-test-')
        self.base = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)
        self.policy = copy.deepcopy(POLICY)
        self.policy['backup']['minimum_free_bytes_after_write'] = 0
        self.artifacts = {'weights': self.base / 'weights.bin', 'trainer_state': self.base / 'trainer.json'}
        self.artifacts['trainer_state'].write_text('{"seed": 42}', encoding='utf-8')
        self.run = EpochRun(self.base / 'run', 'A3', self.policy)

    def finish(self, epoch, correct):
        self.artifacts['weights'].write_bytes(f'weights at epoch {epoch}'.encode())
        return self.run.complete_epoch(epoch, train_loss=100 - epoch, dev_loss=1.,
                                       dev_correct=correct, dev_total=1000, safe=True, artifacts=self.artifacts)

    def test_two_copies_retention_and_best_on_stop(self):
        for e in range(1, 11): result = self.finish(e, 100 if e == 1 else 99)
        self.assertTrue(result['stop'])
        self.assertEqual(Path(result['best_checkpoint']['weights']).read_bytes(), b'weights at epoch 1')
        for copy_name in ('copy-a', 'copy-b'):
            self.assertEqual({p.name for p in (self.run.root / copy_name).iterdir()},
                             {'epoch-000001', 'epoch-000009', 'epoch-000010'})
        a = self.run.root / 'copy-a/epoch-000010/manifest.json'
        b = self.run.root / 'copy-b/epoch-000010/manifest.json'
        self.assertEqual(read(a), read(b))
        lines = (self.run.journal / 'metrics.jsonl').read_text().splitlines()
        self.assertEqual(len(lines), 10)
        resumed = EpochRun(self.run.root, 'A3', self.policy)
        self.assertEqual(resumed.best_checkpoint(), self.run.best_checkpoint())
        self.assertEqual(read(self.run.root / 'final.json')['selected_epoch'], 1)

    def test_corrupt_first_copy_falls_back_to_second(self):
        self.finish(1, 100)
        first = Path(self.run.best_checkpoint()['weights'])
        first.write_bytes(b'corrupted')
        self.assertIn('copy-b', self.run.best_checkpoint()['weights'])
        Path(self.run.best_checkpoint()['weights']).write_bytes(b'also corrupted')
        with self.assertRaises(IOError): self.run.best_checkpoint()

    def test_low_disk_does_not_commit_epoch(self):
        with patch('training_controls.e70p9.epoch_control.shutil.disk_usage') as usage:
            usage.return_value.free = 0
            with self.assertRaisesRegex(OSError, 'INSUFFICIENT'): self.finish(1, 100)
        self.assertFalse(self.run.state_path.exists())
        self.assertFalse((self.run.root / '.epoch.lock').exists())

    def test_publish_failure_preserves_backups_and_can_retry(self):
        class Publisher:
            fail = True
            def publish(self, files, message):
                if self.fail: raise RuntimeError('simulated offline')
                self.files = files
        publisher = Publisher()
        self.run.publisher = publisher
        self.assertFalse(self.finish(1, 100)['github_synced'])
        self.assertTrue(Path(self.run.best_checkpoint()['weights']).exists())
        publisher.fail = False
        self.assertTrue(self.run.sync())
        self.assertEqual(len(publisher.files), 4)

    def test_a2_cannot_be_treated_as_epochs(self):
        with self.assertRaisesRegex(ValueError, 'A2_IS'): EpochRun(self.base / 'a2', 'A2', self.policy)


@unittest.skipUnless(shutil.which('git'), 'Git not installed')
class GitTests(unittest.TestCase):
    def test_preserves_base_tree_and_retries_offline_commit(self):
        with tempfile.TemporaryDirectory(prefix='e70-git-test-') as temporary:
            base = Path(temporary).resolve()
            remote = base / 'remote.git'
            env = dict(os.environ, GIT_AUTHOR_NAME='Test', GIT_COMMITTER_NAME='Test',
                       GIT_AUTHOR_EMAIL='test@example.invalid', GIT_COMMITTER_EMAIL='test@example.invalid')
            def git(*args):
                return subprocess.run(['git', *map(str, args)], env=env, check=True,
                                      capture_output=True, text=True).stdout.strip()
            git('init', '--bare', remote)
            empty = base / 'empty.txt'; empty.write_text('existing project file\n')
            blob = git('--git-dir', remote, 'hash-object', '-w', empty)
            # Seed a local remote using a separate index and the same plumbing as production.
            env['GIT_INDEX_FILE'] = str(base / 'seed.index')
            git('--git-dir', remote, 'read-tree', '--empty')
            git('--git-dir', remote, 'update-index', '--add', '--cacheinfo', '100644', blob, 'README.md')
            tree = git('--git-dir', remote, 'write-tree')
            commit = git('--git-dir', remote, 'commit-tree', tree, '-m', 'test seed')
            git('--git-dir', remote, 'update-ref', 'refs/heads/main', commit)
            git('--git-dir', remote, 'symbolic-ref', 'HEAD', 'refs/heads/main')
            publisher = GitJournal(base / 'journal.git', str(remote), 'codex/test', 'runs/test')
            state = base / 'state.json'; state.write_text('{"epoch": 1}\n')
            first = publisher.publish({'state.json': state}, 'epoch 1')
            self.assertEqual(git('--git-dir', remote, 'show', first + ':README.md'), 'existing project file')
            state.write_text('{"epoch": 2}\n')
            real_git = publisher._git
            def offline(*args, **kwargs):
                if args[0] == 'push': raise RuntimeError('simulated push outage')
                return real_git(*args, **kwargs)
            with patch.object(publisher, '_git', side_effect=offline):
                with self.assertRaises(RuntimeError): publisher.publish({'state.json': state}, 'epoch 2')
            pending = git('--git-dir', publisher.directory, 'rev-parse', 'refs/heads/codex/test')
            self.assertNotEqual(first, pending)
            self.assertEqual(git('--git-dir', remote, 'rev-parse', 'refs/heads/codex/test'), first)
            self.assertEqual(publisher.publish({'state.json': state}, 'epoch 2 retry'), pending)
            self.assertEqual(git('--git-dir', remote, 'rev-parse', 'refs/heads/codex/test'), pending)
            self.assertEqual(git('--git-dir', remote, 'show', pending + ':runs/test/state.json'), '{"epoch": 2}')
            with self.assertRaises(ValueError): publisher.publish({'weights.bin': empty}, 'reject weights')


if __name__ == '__main__':
    unittest.main()
