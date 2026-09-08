"""Matched TRAIN rows, actual emitted positives and full P2 marginal offsets."""
import os
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import collections
import gzip
import json
import math
import time
from pathlib import Path
from s06e_p4 import Tokenizer
from features_p4 import emitted_positives
from .common import ROOT,OLD,DEST,LOCAL,HERE,read,records,digest,atomic_json,require,original_freeze,emit
from .numerics import fit


def main():
    folder=DEST/'rank';require(not folder.exists(),'P4_REFUSE_OVERWRITE_RANK');folder.mkdir()
    cfg=read(HERE/'protocol.json')['rank'];cache=read(LOCAL/'cache-summary.json');headseal=read(LOCAL/'head-selection.json')
    require(cache['status']=='CACHE_COMPLETE' and digest(Path(cache['path']))==cache['sha256'],'P4_MARGINAL_CACHE_CHANGED')
    require(digest(DEST/'head-model.json')==headseal['head_model_sha256'],'P4_RANK_HEAD_CHANGED')
    model=read(DEST/'head-model.json');hs=headseal['head_strength']
    frozen={**read(LOCAL/'head-freeze.json'),**{n:digest(ROOT/n) for n in ['training_controls/layers_p4/fit_rank.py','training_controls/layers_p4/validate.py','training_controls/layers_p4/evaluate_head.py']}}
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_RANK_SOURCE_CHANGED');atomic_json(LOCAL/'rank-freeze.json',frozen)
    runtimes={'base_head':Tokenizer(model=model),'selected_head':Tokenizer(model=model,head_strength=hs)}
    frequencies={k:collections.Counter() for k in runtimes};counts=collections.Counter();start=time.monotonic()
    streams={k:gzip.open(folder/(k+'-features.jsonl.gz'),'wt',encoding='utf-8',compresslevel=3) for k in runtimes}
    try:
        for n,(rec,cache_rec) in enumerate(zip(records(OLD/'train-raw.jsonl.gz'),records(Path(cache['path'])),strict=True),1):
            require(rec['id']==cache_rec['id'],'P4_TRAIN_SCORE_ALIGNMENT');tokens=rec['raw_output']['tokens']
            require(len(tokens)==len(cache_rec['tokens']),'P4_TRAIN_TOKEN_ALIGNMENT')
            for i,t in enumerate(tokens):
                gold=rec['golds'][i]['gold'];aa=t['analysis']['analyses'];m=cache_rec['tokens'][i]['relative_marginals']
                if not gold or not aa:continue
                require(set(m)=={a['analysis_id'] for a in aa},'P4_MISSING_WORD_MARGINALS')
                require(all(math.isfinite(v) for v in m.values()),'P4_NONFINITE_MARGINAL')
                cop=rec['golds'][i]['projection']=='EXPLICIT_SOURCE_NOMINAL_COPULA'
                positive={k:emitted_positives(tokens,i,gold,cop,rt.export_head) for k,rt in runtimes.items()}
                counts['labelled_native_words']+=1
                for k,p in positive.items():counts[k+'_no_emitted_strict_positive']+=not p
                if any(not p or len(p)==len(aa) for p in positive.values()):continue
                counts['common_competitive_words']+=1
                for k,rt in runtimes.items():
                    views=rt.export_head.token(tokens,i);fs=[rt.features.rank(tokens,i,a,views[a['analysis_id']]['view']) for a in aa]
                    good=[a['analysis_id'] in positive[k] for a in aa]
                    require(any(good) and not all(good),'P4_NONCOMPETITIVE_RANK_LABELS')
                    emit(streams[k],{'context_id':rec['id'],'token':i,'features':fs,'good':good,
                                     'offsets':[m[a['analysis_id']] for a in aa],'analysis_ids':[a['analysis_id'] for a in aa]})
                    frequencies[k].update(set().union(*(set(f) for f in fs)))
            if n%200==0 or n==3260:
                print(json.dumps({'stage':'P4_RANK_PREPARE','sentences':n,'examples':counts['common_competitive_words'],'seconds':round(time.monotonic()-start,1)}),flush=True)
                for rt in runtimes.values():rt.head.views.cache.clear()
    finally:
        for stream in streams.values():stream.close()
    require(n==3260,'P4_RANK_TRAIN_COUNT');stats={}
    for k in runtimes:
        if k=='selected_head' and hs==0:
            model['rank_models'][k]=dict(model['rank_models']['base_head']);stats[k]={**stats['base_head'],'identical_head_zero_model_reused':True}
        else:
            model['rank_models'][k],stats[k]=fit(folder/(k+'-features.jsonl.gz'),frequencies[k],cfg)
        model['rank_head_strengths'][k]=0. if k=='base_head' else hs
        print(json.dumps({'stage':'P4_RANK_FIT_COMPLETE','variant':k,**stats[k]}),flush=True)
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_FITTED_SOURCE_CHANGED');original_freeze()
    model['source_sha256']=frozen;model['selected_head_strength']=hs;model['TRAIN_marginals_sha256']=cache['sha256']
    atomic_json(DEST/'model.json',model);meta={'path':str(DEST/'model.json'),'sha256':digest(DEST/'model.json')}
    summary={'status':'RANK_FIT_COMPLETE','head_strength':hs,'counts':dict(counts),'arms':stats,'model_sha256':meta['sha256'],
             'TRAIN_sentences':3260,'DEV_CALIB_TEST_used_in_loss':False,'seconds':round(time.monotonic()-start,1)}
    atomic_json(LOCAL/'model-location.json',meta);atomic_json(LOCAL/'rank-fit-summary.json',summary);atomic_json(folder/'fit-summary.json',summary)


if __name__=='__main__':main()
