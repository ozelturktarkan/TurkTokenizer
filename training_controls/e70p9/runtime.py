"""Production factory: run data and Git objects must remain on V:."""
import os
import re
from pathlib import Path

from .epoch_control import EpochRun, read
from .git_journal import GitJournal


def open_run(run_id, stage):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', run_id):
        raise ValueError('INVALID_RUN_ID')
    policy = read(Path(__file__).with_name('protocol.json'))
    base = Path(policy['backup']['root'])
    if os.name != 'nt' or base.drive.upper() != 'V:' or not Path('V:/').is_dir():
        raise OSError('V_BACKUP_DRIVE_REQUIRED')
    if stage not in policy['epoch_stages']:
        raise ValueError('A2_IS_CALIBRATION_NOT_EPOCH_TRAINING')
    run_root = base / 'runs' / run_id / stage
    if run_root.resolve().drive.upper() != 'V:':
        raise ValueError('BACKUP_PATH_ESCAPES_V_DRIVE')
    publisher = GitJournal(base / 'git' / (run_id + '-' + stage + '.git'),
                           policy['github']['remote'],
                           policy['github']['branch_prefix'] + run_id + '-' + stage,
                           'training-runs/' + run_id + '/' + stage)
    return EpochRun(run_root, stage, policy, publisher)
