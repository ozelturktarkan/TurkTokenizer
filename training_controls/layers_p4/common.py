import gzip
import json
from pathlib import Path
from bootstrap import ROOT
from training_controls.grammar_p3.common import PARENT,original_freeze as parent_freeze,records,emit
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import require
from training_controls.a3_epoch.train import check_output

OLD=PARENT/'P3-yont-v1'
DEST=PARENT/'P4-two-layer-v1'
LOCAL=ROOT/'results_layers_p4'
HERE=ROOT/'training_controls/layers_p4'
BASE=PARENT/'P2-lexical-v1/policy-imst/evaluation/1.00'


def original_freeze():
    out=parent_freeze();receipt=read(ROOT/'results_grammar_p3/backup-receipt.json')
    for name,expected in receipt['sha256'].items():
        path=ROOT/name[len('source/'):] if name.startswith('source/') else OLD/name
        require(digest(path)==expected,'P4_PARENT_P3_CHANGED:'+name)
    out['P3_receipt_sha256']=digest(ROOT/'results_grammar_p3/backup-receipt.json')
    return out


def save_rows(path,rows):
    with gzip.open(path,'wt',encoding='utf-8',compresslevel=3) as f:
        for row in rows:emit(f,row)
