"""Back up and publish this exact policy package. Does not start training."""
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .epoch_control import atomic_json, digest, read
from .git_journal import GitJournal


FILES = ('__init__.py', 'epoch_control.py', 'git_journal.py', 'runtime.py',
         'protocol.json', 'README.md', 'test_controls.py', 'prepare.py')


def main():
    source = Path(__file__).resolve().parent
    policy = read(source / 'protocol.json')
    base = Path(policy['backup']['root'])
    if os.name != 'nt' or base.drive.upper() != 'V:' or not Path('V:/').is_dir():
        raise OSError('V_BACKUP_DRIVE_REQUIRED')
    if base.resolve().drive.upper() != 'V:': raise ValueError('BACKUP_PATH_ESCAPES_V')
    base.mkdir(parents=True, exist_ok=True)
    files = {name: source / name for name in FILES}
    hashes = {name: digest(path) for name, path in files.items()}
    size = sum(path.stat().st_size for path in files.values())
    if shutil.disk_usage(base).free < 2 * size + policy['backup']['minimum_free_bytes_after_write']:
        raise OSError('INSUFFICIENT_BACKUP_SPACE')
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    package_root = base / 'prepared' / timestamp
    package_root.mkdir(parents=True, exist_ok=False)
    for copy_name in ('copy-a', 'copy-b'):
        destination = package_root / copy_name
        destination.mkdir()
        for name, path in files.items():
            target = destination / name
            shutil.copyfile(path, target)
            with target.open('r+b') as dst: os.fsync(dst.fileno())
            if digest(target) != hashes[name]: raise IOError('PACKAGE_BACKUP_HASH_MISMATCH')
        atomic_json(destination / 'sha256.json', hashes)
    branch = 'codex/e70-p9-policy'
    publisher = GitJournal(base / 'git' / 'policy.git', policy['github']['remote'], branch,
                           'training_controls/e70p9', allowed_files=FILES)
    receipt = {'status': 'BACKED_UP', 'package_backup': str(package_root), 'copies': 2,
               'sha256': hashes, 'training_started': False, 'existing_trainer_modified': False,
               'remote': policy['github']['remote'], 'branch': branch}
    atomic_json(source / 'preparation-receipt.json', receipt)
    try:
        commit = publisher.publish(files, 'Add E70/P9 safe checkpoint and V-drive training controls')
        receipt.update(status='BACKED_UP_AND_PUSHED', commit=commit,
                       url='https://github.com/ozelturktarkan/TurkTokenizer/commit/' + commit)
    except Exception as exc:
        receipt.update(status='BACKED_UP_GITHUB_PENDING', error_type=type(exc).__name__)
    atomic_json(source / 'preparation-receipt.json', receipt)
    atomic_json(package_root / 'preparation-receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
