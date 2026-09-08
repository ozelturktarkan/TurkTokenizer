"""IMST-only head with verified reuse of the mixed experiment feature rows."""
import os
for var in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[var]='1'
import collections
import gzip
import json
import time
import numpy as np
from scipy.optimize import minimize
from analyzer_s06e_p1 import PhonologyAnalyzer
from analysis_schema_p2 import LexicalViews,view_matches,VERSION
from context_ranker import canonical
from training_controls.a1_epoch.numerics import records,matrix,objective
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import require
from .fit import ROOT,DEST,LOCAL,HERE


def main():
    dest=DEST/'policy-imst'; local=LOCAL/'policy-imst'
    require(not dest.exists() and not local.exists(),'P2_POLICY_REFUSE_OVERWRITE')
    config=read(HERE/'policy-protocol.json'); freeze=read(LOCAL/'freeze.json')
    require(all(digest(ROOT/n)==h for n,h in freeze['sources'].items()),'P2_SCHEMA_CHANGED')
    cache=ROOT/'results_a123/fit/train-candidates.jsonl.gz'
    require(digest(cache)==freeze['TRAIN_cache_sha256'],'P2_CACHE_CHANGED')
    dest.mkdir(); local.mkdir(); sources={n:digest(ROOT/n) for n in [
        'training_controls/lexical_p2/fit_policy.py','training_controls/lexical_p2/policy-protocol.json']}
    atomic_json(local/'freeze.json',{'sources':sources,'mixed_freeze_sha256':digest(LOCAL/'freeze.json'),
        'mixed_features_sha256':digest(DEST/'train-features.jsonl.gz'),'E05_sha256':freeze['E05_sha256']})
    views=LexicalViews(PhonologyAnalyzer('combined')); prior_rows=iter(records(DEST/'train-features.jsonl.gz'))
    frequencies=collections.Counter(); counts=collections.Counter(); ids=set(); started=time.monotonic()
    features=dest/'features.jsonl.gz'
    with gzip.open(features,'wt',encoding='utf-8',compresslevel=3) as out:
        for rec in records(cache):
            if rec['corpus']=='IMST': ids.add(rec['id'])
            for t in rec['tokens']:
                gold=t.get('gold'); aa=t['analysis']['analyses']
                if not gold or not aa or not t['analysis']['search_complete']: continue
                good=[]
                for a in {canonical(a):a for a in aa}.values():
                    good.extend(view_matches(v,gold,True,t['projection']=='EXPLICIT_SOURCE_NOMINAL_COPULA',a) for v in views.options(a))
                if not any(good) or all(good): continue
                row=next(prior_rows); counts['verified_mixed_rows']+=1
                require(row['good']==good,'P2_POLICY_FEATURE_ALIGNMENT')
                if rec['corpus']!='IMST': continue
                out.write(json.dumps(row,ensure_ascii=False)+'\n')
                frequencies.update(set().union(*(set(x) for x in row['features'])))
                counts['examples']+=1; counts['view_rows']+=len(good)
            if len(views.cache)>30000: views.cache.clear()
    require(next(prior_rows,None) is None and counts['verified_mixed_rows']==60389,'P2_POLICY_INCOMPLETE_PARENT')
    require(len(ids)==3260,'P2_IMST_TRAIN_COUNT')
    vocab={k:i for i,k in enumerate(sorted(k for k,n in frequencies.items() if n>=3))}
    data=matrix(records(features),vocab); reg=config['optimizer']['regularization']; history=[]
    def callback(w):
        history.append(objective(w,data,reg,False))
        if len(history)%20==0: print(json.dumps({'stage':'IMST_FIT','iteration':len(history),'loss':history[-1]}),flush=True)
    initial=objective(np.zeros(len(vocab)),data,reg,False)
    fit=minimize(lambda w:objective(w,data,reg),np.zeros(len(vocab)),jac=True,method='L-BFGS-B',callback=callback,
        options={'maxiter':100,'ftol':1e-9})
    require(np.isfinite(fit.x).all() and fit.fun<initial,'P2_POLICY_FIT_INVALID')
    require(all(digest(ROOT/n)==h for n,h in sources.items()),'P2_POLICY_SOURCE_CHANGED')
    model={'version':'S06E-P2-IMST-HEAD-1','schema':VERSION,'export_policy':'UD_IMST',
        'E05_sha256':freeze['E05_sha256'],'weights':{k:float(fit.x[i]) for k,i in vocab.items()},'TRAIN_only':True,
        'TRAIN_sentences':len(ids),'source_corpus':'IMST'}
    atomic_json(dest/'head.json',model)
    meta={'path':str(dest/'head.json'),'sha256':digest(dest/'head.json'),'export_policy':'UD_IMST'}
    summary={'status':'FIT_COMPLETE','counts':dict(counts),'TRAIN_sentences':len(ids),'features':len(vocab),
        'initial_loss':initial,'final_loss':float(fit.fun),'optimizer_success':bool(fit.success),
        'optimizer_message':str(fit.message),'iterations':int(fit.nit),'loss_history':history,
        'model_sha256':meta['sha256'],'seconds':round(time.monotonic()-started,1),'TEST_opened':False}
    atomic_json(local/'model-location.json',meta); atomic_json(dest/'fit-summary.json',summary)
    atomic_json(local/'fit-summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='loss_history'}),flush=True)


if __name__=='__main__': main()
