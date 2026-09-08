"""Isolated epoch controller; never launches or modifies an existing trainer."""
import hashlib
import json
import math
import os
import re
import shutil
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as src:
        return hashlib.file_digest(src, 'sha256').hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as dst:
        json.dump(value, dst, ensure_ascii=False, indent=2, allow_nan=False)
        dst.write('\n'); dst.flush(); os.fsync(dst.fileno())
    os.replace(temporary, path)


def advance(previous, epoch, train_loss, dev_loss, dev_correct, dev_total, safe, policy):
    if previous and previous['stop']:
        raise ValueError('RUN_ALREADY_STOPPED')
    if type(epoch) is not int or epoch != (previous['epoch'] + 1 if previous else 1):
        raise ValueError('EPOCH_SEQUENCE')
    if not all(math.isfinite(v) for v in (train_loss, dev_loss)):
        raise ValueError('NONFINITE_LOSS')
    if type(dev_correct) is not int or type(dev_total) is not int or not 0 <= dev_correct <= dev_total or dev_total == 0:
        raise ValueError('DEV_COUNTS')
    if type(safe) is not bool:
        raise ValueError('SAFETY_FLAG_REQUIRED')
    if previous and previous['dev_total'] != dev_total:
        raise ValueError('DEV_DENOMINATOR_CHANGED')
    best_count = previous['best_correct'] if previous else -1
    better = safe and dev_correct > best_count
    best_epoch = epoch if better else (previous['best_epoch'] if previous else None)
    best_count = dev_correct if better else best_count
    patience = 0 if better else (previous['patience_count'] if previous else 0) + 1
    of = policy['overfitting']; epsilon = of['loss_epsilon']
    signal = bool(previous and epoch >= of['first_monitored_epoch']
                  and train_loss < previous['train_loss'] - epsilon
                  and dev_loss > previous['dev_loss'] + epsilon and dev_correct < best_count)
    streak = previous['overfit_count'] + 1 if signal else 0
    reason = ('OVERFITTING_3' if streak >= of['consecutive_signals'] else
              'PATIENCE_9' if patience >= policy['patience'] else
              'MAX_EPOCH_70' if epoch >= policy['max_epochs_per_stage'] else None)
    return {'epoch': epoch, 'train_loss': float(train_loss), 'dev_loss': float(dev_loss),
            'dev_correct': dev_correct, 'dev_total': dev_total, 'dev_accuracy': dev_correct / dev_total,
            'safe': safe, 'new_best': better, 'best_correct': best_count, 'best_epoch': best_epoch,
            'patience_count': patience, 'overfit_signal': signal, 'overfit_count': streak,
            'stop': reason is not None, 'stop_reason': reason}


class EpochRun:
    def __init__(self, root, stage, policy, publisher=None):
        if stage not in policy['epoch_stages']:
            raise ValueError('A2_IS_CALIBRATION_NOT_EPOCH_TRAINING')
        if Path(root).is_symlink(): raise ValueError('SYMLINK_RUN_ROOT')
        self.root = Path(root).resolve(); self.stage = stage; self.policy = policy; self.publisher = publisher
        self.root.mkdir(parents=True, exist_ok=True)
        self.policy_hash = hashlib.sha256(json.dumps(policy, sort_keys=True).encode()).hexdigest()
        self.state_path = self.root / 'state.json'
        self.state = read(self.state_path) if self.state_path.exists() else None
        if self.state and (self.state['policy_sha256'] != self.policy_hash or self.state['stage'] != stage):
            raise ValueError('RUN_POLICY_CHANGED')
        self.journal = self.root / 'journal'; self.journal.mkdir(exist_ok=True)
        self.events = self.root / 'events'; self.events.mkdir(exist_ok=True)

    def _inside(self, path):
        path = Path(path)
        if path.is_symlink() or not path.resolve().is_relative_to(self.root) or path.resolve() == self.root:
            raise ValueError('UNSAFE_SNAPSHOT_PATH')
        return path

    def _snapshot(self, copy_name, state, artifacts):
        folder = self._inside(self.root / copy_name / f"epoch-{state['epoch']:06d}")
        folder.mkdir(parents=True, exist_ok=False)
        receipt = {}
        for key, source in artifacts.items():
            if not re.fullmatch(r'[a-z][a-z0-9_-]*', key): raise ValueError('ARTIFACT_KEY')
            destination = self._inside(folder / (key + '.checkpoint'))
            expected = digest(source)
            shutil.copyfile(source, destination)
            with destination.open('r+b') as dst: os.fsync(dst.fileno())
            if digest(destination) != expected: raise IOError('CHECKPOINT_HASH_MISMATCH')
            receipt[key] = {'file': destination.name, 'sha256': expected, 'bytes': destination.stat().st_size}
        atomic_json(folder / 'state.json', state)
        atomic_json(folder / 'manifest.json', {'format': 'E70_SNAPSHOT_1', 'artifacts': receipt,
                                              'state_sha256': digest(folder / 'state.json')})
        return folder

    def _prune(self, state):
        keep = {state['epoch'], max(1, state['epoch'] - 1), state['best_epoch']}
        for copy_name in self.policy['backup']['copies']:
            for folder in (self.root / copy_name).glob('epoch-*'):
                if not re.fullmatch(r'epoch-\d{6}', folder.name) or int(folder.name[6:]) in keep: continue
                self._inside(folder)
                manifest = read(folder / 'manifest.json')
                if manifest['format'] != 'E70_SNAPSHOT_1': raise ValueError('NOT_OWN_SNAPSHOT')
                allowed = {v['file'] for v in manifest['artifacts'].values()} | {'state.json', 'manifest.json'}
                if {p.name for p in folder.iterdir()} != allowed: raise ValueError('UNEXPECTED_SNAPSHOT_FILES')
                for p in folder.iterdir(): self._inside(p).unlink()
                folder.rmdir()

    def best_checkpoint(self):
        if not self.state or self.state['best_epoch'] is None: return None
        for copy_name in self.policy['backup']['copies']:
            folder = self._inside(self.root / copy_name / f"epoch-{self.state['best_epoch']:06d}")
            try:
                manifest = read(folder / 'manifest.json')
                if digest(folder / 'state.json') != manifest['state_sha256']: continue
                if all(digest(self._inside(folder / a['file'])) == a['sha256'] for a in manifest['artifacts'].values()):
                    return {k: str(folder / a['file']) for k, a in manifest['artifacts'].items()}
            except (OSError, ValueError, KeyError):
                continue
        raise IOError('BOTH_BEST_COPIES_INVALID')

    def _journal_files(self):
        # Fixed allowlist: arbitrary trainer output and credentials cannot be staged.
        return {name: self.journal / name for name in
                ('state.json', 'metrics.jsonl', 'training.log', 'checkpoint-sha256.json')}

    def sync(self):
        """Retry publication, including after the last epoch; no new epoch is needed."""
        if not self.publisher or not self.state: return None
        try:
            self.publisher.publish(self._journal_files(), f"{self.stage} epoch {self.state['epoch']:02d}")
            synced = True
        except Exception:
            # Never publish authentication output or arbitrary stderr.
            synced = False
        atomic_json(self.root / 'github-sync.json', {'synced': synced, 'latest_epoch': self.state['epoch']})
        return synced

    def _write_journal(self, state, manifest):
        # Immutable small events outlive weight retention. Rebuilding is idempotent.
        atomic_json(self.events / f"epoch-{state['epoch']:06d}.json", state)
        atomic_json(self.journal / 'state.json', state)
        atomic_json(self.journal / 'checkpoint-sha256.json', manifest)
        history = [read(self.events / f'epoch-{n:06d}.json') for n in range(1, state['epoch'] + 1)]
        metrics = ''.join(json.dumps(s, ensure_ascii=False, allow_nan=False) + '\n' for s in history)
        logs = ''.join(f"{self.stage} E{s['epoch']:02d}/70 train_loss={s['train_loss']:.8g} "
                       f"dev_loss={s['dev_loss']:.8g} DEV={s['dev_correct']}/{s['dev_total']} "
                       f"patience={s['patience_count']}/9 overfit={s['overfit_count']}/3 "
                       f"best=E{s['best_epoch']} stop={s['stop_reason']}\n" for s in history)
        for name, content in (('metrics.jsonl', metrics), ('training.log', logs)):
            temporary = self.journal / (name + '.tmp')
            with temporary.open('w', encoding='utf-8', newline='\n') as dst:
                dst.write(content); dst.flush(); os.fsync(dst.fileno())
            os.replace(temporary, self.journal / name)

    def complete_epoch(self, epoch, *, train_loss, dev_loss, dev_correct, dev_total, safe, artifacts):
        if 'weights' not in artifacts or 'trainer_state' not in artifacts:
            raise ValueError('WEIGHTS_AND_TRAINER_STATE_REQUIRED')
        if any(not re.fullmatch(r'[a-z][a-z0-9_-]*', k) for k in artifacts): raise ValueError('ARTIFACT_KEY')
        if any(not Path(p).is_file() for p in artifacts.values()): raise ValueError('ARTIFACT_MISSING')
        lock = self.root / '.epoch.lock'
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(descriptor)
        try:
            on_disk = read(self.state_path) if self.state_path.exists() else None
            if on_disk != self.state: raise ValueError('STALE_RUN_STATE')
            state = advance(self.state, epoch, train_loss, dev_loss, dev_correct, dev_total, safe, self.policy)
            state.update(stage=self.stage, policy_sha256=self.policy_hash)
            size = sum(Path(p).stat().st_size for p in artifacts.values())
            if shutil.disk_usage(self.root).free < 2 * size + self.policy['backup']['minimum_free_bytes_after_write'] + 1048576:
                raise OSError('INSUFFICIENT_BACKUP_SPACE')
            folders = [self._snapshot(name, state, artifacts) for name in self.policy['backup']['copies']]
            if read(folders[0] / 'manifest.json') != read(folders[1] / 'manifest.json'):
                raise IOError('BACKUP_COPIES_DIFFER')
            atomic_json(self.events / f'epoch-{epoch:06d}.json', state)
            atomic_json(self.state_path, state); self.state = state
            self._write_journal(state, read(folders[0] / 'manifest.json'))
            self._prune(state)
            best = self.best_checkpoint()
            if state['stop']:
                atomic_json(self.root / 'final.json', {'selected_epoch': state['best_epoch'], 'artifacts': best,
                    'reason': state['stop_reason'], 'status': 'BEST_SAFE_FROZEN' if best else 'FAILED_NO_SAFE_CHECKPOINT'})
            synced = self.sync()
            return {**state, 'best_checkpoint': best, 'github_synced': synced}
        finally:
            lock.unlink()
