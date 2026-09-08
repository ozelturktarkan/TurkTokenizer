import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import json
import time
import sys
from bootstrap import ROOT
sys.path[:0]=[str(ROOT/'.deps-s06'),str(ROOT/'.deps-s05six')]
import numpy as np
from scipy.optimize import minimize
from training_controls.a1_epoch.numerics import matrix,objective
from .common import ROOT,DEST,LOCAL,HERE,read,records,digest,atomic_json,require,original_freeze


def main():
    require(not (DEST/'local-model.json').exists(),'P3_REFUSE_OVERWRITE_LOCAL_MODEL')
    prep=read(LOCAL/'prepare-summary.json');frozen=read(LOCAL/'prepare-freeze.json')
    require(all(digest(ROOT/n)==h for n,h in frozen['source_sha256'].items()),'P3_FEATURE_SOURCE_CHANGED')
    path=DEST/'local-features.jsonl.gz'
    require(digest(path)==prep['artifacts'][path.name],'P3_FEATURE_ROWS_CHANGED')
    cfg=read(HERE/'protocol.json')['A1'];frequencies=read(DEST/'feature-frequencies.json');model=read(DEST/'base-model.json')
    results={};started=time.monotonic()
    for arm in ('government','agreement','combined'):
        keys=sorted(k for k,n in frequencies.items() if n>=cfg['minimum_feature_frequency'] and (arm=='combined' or json.loads(k)[0]==arm))
        vocab={k:i for i,k in enumerate(keys)};data=matrix(records(path),vocab)
        initial=objective(np.zeros(len(vocab)),data,cfg['regularization'],False)
        fit=minimize(lambda w:objective(w,data,cfg['regularization']),np.zeros(len(vocab)),jac=True,method='L-BFGS-B',
                     options={'maxiter':cfg['maxiter'],'ftol':1e-9})
        require(np.isfinite(fit.x).all() and fit.fun<=initial+1e-9,'P3_LOCAL_FIT_INVALID')
        model['local_models'][arm]={k:float(fit.x[i]) for k,i in vocab.items()}
        results[arm]={'examples':len(data[1]),'features':len(keys),'initial_loss':initial,'final_loss':float(fit.fun),
                      'iterations':int(fit.nit),'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message)}
        print(json.dumps({'stage':'P3_A1_COMPLETE','arm':arm,**results[arm]},ensure_ascii=False),flush=True)
    require(all(digest(ROOT/n)==h for n,h in frozen['source_sha256'].items()),'P3_LOCAL_SOURCE_CHANGED')
    original_freeze();atomic_json(DEST/'local-model.json',model)
    result={'status':'LOCAL_FIT_COMPLETE','arms':results,'seconds':round(time.monotonic()-started,1),
            'model_sha256':digest(DEST/'local-model.json'),'fit_source_sha256':digest(HERE/'fit_local.py'),'TEST_opened':False}
    atomic_json(LOCAL/'local-fit-summary.json',result);atomic_json(DEST/'local-fit-summary.json',result)


if __name__=='__main__':main()
