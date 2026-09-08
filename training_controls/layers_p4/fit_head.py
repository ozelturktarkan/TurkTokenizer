"""Conditional lexical view loss, independent of native candidate ranking."""
import os
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import collections
import gzip
import json
import time
from s06e_p2_policy import Tokenizer
from analysis_schema_p2 import view_matches,view_features
from features_p4 import Features,VERSION
from .common import ROOT,OLD,DEST,LOCAL,HERE,read,records,digest,atomic_json,require,original_freeze,emit
from .numerics import fit


def main():
    folder=DEST/'head';require(not folder.exists(),'P4_REFUSE_OVERWRITE_HEAD');folder.mkdir()
    paths=['features_p4.py','s06e_p4.py','training_controls/layers_p4/fit_head.py','training_controls/layers_p4/numerics.py']
    frozen={n:digest(ROOT/n) for n in paths};atomic_json(LOCAL/'head-freeze.json',frozen)
    cfg=read(HERE/'protocol.json')['head'];rt=Tokenizer(1.);frames=read(OLD/'base-model.json')['frame_counts'];features=Features(frames)
    source=OLD/'train-raw.jsonl.gz';require(digest(source)==read(ROOT/'results_grammar_p3/prepare-summary.json')['artifacts']['train-raw.jsonl.gz'],'P4_HEAD_CACHE_CHANGED')
    frequencies=collections.Counter();counts=collections.Counter();start=time.monotonic()
    with gzip.open(folder/'features.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as stream:
        for n,rec in enumerate(records(source),1):
            tokens=rec['raw_output']['tokens']
            for i,t in enumerate(tokens):
                gold=rec['golds'][i]['gold'];rows=[];wordfeatures=set()
                if not gold:continue
                for a in t['analysis']['analyses']:
                    vv=rt.head.views.options(a);good=[view_matches(v,gold) for v in vv]
                    if not any(good) or all(good):continue
                    fs=[features.view(tokens,i,a,v) for v in vv]
                    offsets=[sum(rt.head.weights.get(k,0.)*x for k,x in view_features(tokens,i,a,v).items()) for v in vv]
                    rows.append({'context_id':rec['id'],'token':i,'analysis_id':a['analysis_id'],
                                 'features':fs,'good':good,'offsets':offsets})
                    wordfeatures.update(set().union(*(set(x) for x in fs)))
                for row in rows:row['weight']=1./len(rows);emit(stream,row)
                counts['conditional_native_examples']+=len(rows);counts['competitive_words']+=bool(rows)
                frequencies.update(wordfeatures)
            if n%200==0 or n==3260:
                print(json.dumps({'stage':'P4_HEAD_PREPARE','sentences':n,'words':counts['competitive_words'],'seconds':round(time.monotonic()-start,1)}),flush=True)
                rt.head.views.cache.clear()
    require(n==3260,'P4_HEAD_SENTENCE_COUNT');atomic_json(folder/'frequencies.json',dict(frequencies))
    weights,stats=fit(folder/'features.jsonl.gz',frequencies,cfg)
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_HEAD_SOURCE_CHANGED');original_freeze()
    model={'version':VERSION,'P2_head_sha256':rt.head.sha256,'frames':frames,'view_weights':weights,
           'rank_models':{},'rank_head_strengths':{},'TRAIN_sentences':3260,'TRAIN_only':True,
           'head_target':'CONDITIONAL_LEMMA_POS_WITHIN_NATIVE_ANALYSIS','head_source_sha256':frozen}
    atomic_json(DEST/'head-model.json',model)
    result={'status':'HEAD_FIT_COMPLETE','counts':dict(counts),'fit':stats,'model_sha256':digest(DEST/'head-model.json'),
            'seconds':round(time.monotonic()-start,1),'TEST_opened':False}
    atomic_json(LOCAL/'head-fit-summary.json',result);atomic_json(folder/'fit-summary.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
