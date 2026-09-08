"""TRAIN-only partial-label residual head over trace-backed lexical views."""
import os
for var in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[var]='1'
import collections
import gzip
import json
import math
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps-s06'),str(ROOT/'.deps-s05six')]
import numpy as np
from scipy.optimize import minimize
from analyzer_s06e_p1 import PhonologyAnalyzer
from analysis_schema_p2 import LexicalViews, view_features, view_matches, VERSION
from s06e_p1 import DEFAULT_RANKER,E05_SHA256
from s06e_a123 import WeightedRanker
from context_ranker import canonical
from training_controls.a1_epoch.numerics import records,vocabulary,matrix,objective
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import verify_freeze, require

HERE=Path(__file__).resolve().parent
PARENT=DEFAULT_RANKER.parent.parent
DEST=PARENT/'P2-lexical-v1'
LOCAL=ROOT/'results_lexical_p2'
SOURCES=['analysis_schema_p2.py', 'training_controls/lexical_p2/fit.py',
         'training_controls/lexical_p2/protocol.json','training_controls/lexical_p2/test_schema.py']


def main():
    require(not DEST.exists() and not LOCAL.exists(),'P2_REFUSE_OVERWRITE')
    config=read(HERE/'protocol.json'); manifest=read(ROOT/'training/a1-large-v1/manifest.json')
    verify_freeze(PARENT/'A2',read(PARENT/'A2/freeze.json'))
    cache=ROOT/'results_a123/fit/train-candidates.jsonl.gz'
    require(digest(cache)==read(ROOT/'results_a123/fit/prepare-summary.json')['cache_sha256'],'P2_TRAIN_CACHE_CHANGED')
    require(digest(ROOT/'training/a1-large-v1/train.jsonl')==manifest['files']['train.jsonl'],'P2_TRAIN_CHANGED')
    require(digest(DEFAULT_RANKER)==E05_SHA256,'P2_E05_CHANGED')
    train_ids={json.loads(x)['id'] for x in (ROOT/'training/a1-large-v1/train.jsonl').read_text(encoding='utf-8').splitlines()}
    DEST.mkdir(); LOCAL.mkdir()
    frozen={'sources':{n:digest(ROOT/n) for n in SOURCES},'TRAIN_sha256':manifest['files']['train.jsonl'],
            'TRAIN_cache_sha256':digest(cache),'E05_sha256':E05_SHA256,
            'parent_freeze_sha256':digest(PARENT/'A2/freeze.json'),'TRAIN_sentences':len(train_ids),
            'fit_reads_DEV_CALIB_TEST':False}
    atomic_json(DEST/'freeze.json',frozen); atomic_json(LOCAL/'freeze.json',frozen)
    analyzer=PhonologyAnalyzer('combined'); views=LexicalViews(analyzer)
    base=WeightedRanker(read(DEFAULT_RANKER),1.)
    started=time.monotonic(); counts=collections.Counter(); seen=set(); frequencies=collections.Counter()
    path=DEST/'train-features.jsonl.gz'
    with gzip.open(path,'wt',encoding='utf-8',compresslevel=3) as stream:
        for rec in records(cache):
            require(rec['id'] in train_ids and rec['id'] not in seen,'P2_TRAIN_MEMBERSHIP'); seen.add(rec['id'])
            # Cached TRAIN inventories are the frozen R5 candidates. The view
            # head does not consume P1-only unseen paths during fitting.
            tokens=[{k:t[k] for k in ('raw','start','end','analysis')} for t in rec['tokens']]
            for i,t in enumerate(rec['tokens']):
                gold=t.get('gold'); aa=t['analysis']['analyses']
                if not gold or not aa or not t['analysis']['search_complete']: continue
                unique={canonical(a):a for a in aa}; options=[]; good=[]; fs=[]; offsets=[]
                base_scores=base.token(tokens,i)
                for a in unique.values():
                    for v in views.options(a):
                        options.append(v)
                        good.append(view_matches(v,gold,True,t['projection']=='EXPLICIT_SOURCE_NOMINAL_COPULA',a))
                        fs.append(view_features(tokens,i,a,v)); offsets.append(base_scores[a['analysis_id']])
                counts['labeled_words']+=1
                if not any(good): counts['no_matching_view']+=1; continue
                counts['view_covered_words']+=1
                if all(good): counts['noncompetitive_words']+=1; continue
                row={'features':fs,'good':good,'offsets':offsets}
                stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                frequencies.update(set().union(*(set(x) for x in fs)))
                counts['examples']+=1; counts['view_rows']+=len(fs)
            if len(seen)%500==0:
                print(json.dumps({'stage':'TRAIN_FEATURES','sentences':len(seen),'total':len(train_ids),'seconds':round(time.monotonic()-started,1)},ensure_ascii=False),flush=True)
                views.cache.clear()
    require(seen==train_ids,'P2_TRAIN_PASS_INCOMPLETE')
    vocab={k:i for i,k in enumerate(sorted(k for k,n in frequencies.items() if n>=config['optimizer']['min_feature_frequency']))}
    atomic_json(DEST/'vocabulary.json',vocab)
    data=matrix(records(path),vocab)
    print(json.dumps({'stage':'OPTIMIZE','features':len(vocab),'counts':dict(counts),'nonzeros':data[0].nnz}),flush=True)
    reg=config['optimizer']['regularization']; history=[]
    def fun(w): return objective(w,data,reg)
    def callback(w):
        val=objective(w,data,reg,False); history.append(val)
        if len(history)%10==0: print(json.dumps({'stage':'OPTIMIZE','iteration':len(history),'loss':val}),flush=True)
    initial=objective(np.zeros(len(vocab)),data,reg,False)
    result=minimize(fun,np.zeros(len(vocab)),jac=True,method='L-BFGS-B',callback=callback,
                    options={'maxiter':config['optimizer']['maxiter'],'ftol':1e-9})
    require(np.isfinite(result.x).all() and result.fun<initial,'P2_FIT_INVALID')
    require(all(digest(ROOT/n)==h for n,h in frozen['sources'].items()),'P2_SOURCE_CHANGED_DURING_FIT')
    model={'version':'S06E-P2-HEAD-1','schema':VERSION,'weights':{k:float(result.x[i]) for k,i in vocab.items()},
           'TRAIN_only':True,'E05_sha256':E05_SHA256,'freeze_sha256':digest(DEST/'freeze.json')}
    atomic_json(DEST/'head.json',model)
    summary={'status':'FIT_COMPLETE','counts':dict(counts),'features':len(vocab),'candidate_view_rows':len(data[3]),
             'initial_loss':initial,'final_loss':float(result.fun),'optimizer_success':bool(result.success),
             'optimizer_message':str(result.message),'iterations':int(result.nit),'loss_history':history,
             'model_sha256':digest(DEST/'head.json'),'seconds':round(time.monotonic()-started,1),'training_sentences':len(seen),
             'TRAIN_cache_uses_frozen_R5_candidates':True,'new_morphological_paths':False,'TEST_opened':False}
    atomic_json(DEST/'fit-summary.json',summary); atomic_json(LOCAL/'fit-summary.json',summary)
    atomic_json(LOCAL/'model-location.json',{'path':str(DEST/'head.json'),'sha256':summary['model_sha256']})
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__=='__main__': main()
