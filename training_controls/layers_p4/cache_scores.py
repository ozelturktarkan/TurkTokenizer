"""Cache only label-free full P2 score marginals on frozen TRAIN candidates."""
import gzip
import json
import time
from s06e_p2_policy import Tokenizer
from .common import ROOT,OLD,DEST,LOCAL,HERE,read,digest,atomic_json,require,records,emit,original_freeze,check_output


def main():
    folder=DEST/'cache-r1'
    require(not folder.exists(),'P4_REFUSE_OVERWRITE_CACHE');folder.mkdir(parents=True);LOCAL.mkdir(exist_ok=True)
    source=OLD/'train-raw.jsonl.gz';old=read(ROOT/'results_grammar_p3/prepare-summary.json')
    require(digest(source)==old['artifacts']['train-raw.jsonl.gz'],'P4_TRAIN_CACHE_CHANGED')
    names=['training_controls/layers_p4/common.py','training_controls/layers_p4/cache_scores.py','training_controls/layers_p4/protocol.json']
    frozen={'parents':original_freeze(),'TRAIN_cache_sha256':digest(source),'source_sha256':{n:digest(ROOT/n) for n in names},'TEST_opened':False}
    atomic_json(LOCAL/'cache-freeze-r1.json',frozen);atomic_json(folder/'cache-freeze.json',frozen)
    rt=Tokenizer(1.);start=time.monotonic();n=0;blocks=0;candidates=0
    with gzip.open(folder/'train-marginals.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as f:
        for rec in records(source):
            raw=rec['raw_output'];out=rt.analyze_prepared(raw);blocks+=check_output(rt,raw,out)
            scores=[]
            for i,t in enumerate(raw['tokens']):
                m=rt.context_selector.s06e_marginals.get(i,{})
                ids={a['analysis_id'] for a in t['analysis']['analyses']}
                if m:
                    require(set(m)==ids or (not ids and set(m)=={''}),'P4_MARGINAL_CANDIDATE_MISMATCH')
                    if not ids:m={}
                maximum=max(m.values(),default=0.)
                scores.append({'relative_marginals':{aid:value-maximum for aid,value in m.items()},
                               'preferred_id':out['tokens'][i].get('context_decision',{}).get('preferred_analysis',{}).get('analysis_id') if out['tokens'][i].get('context_decision',{}).get('preferred_analysis') else None})
                candidates+=len(m)
            emit(f,{'id':rec['id'],'tokens':scores});n+=1
            if n%100==0 or n==3260:print(json.dumps({'stage':'P4_TRAIN_MARGINALS','sentences':n,'total':3260,'seconds':round(time.monotonic()-start,1)}),flush=True)
            if n%200==0:rt.head.views.cache.clear()
    require(n==3260,'P4_TRAIN_COUNT');original_freeze()
    require(all(digest(ROOT/n)==h for n,h in frozen['source_sha256'].items()),'P4_CACHE_SOURCE_CHANGED')
    summary={'status':'CACHE_COMPLETE','TRAIN_sentences':n,'candidate_marginals':candidates,'objective_blocks':blocks,
             'path':str(folder/'train-marginals.jsonl.gz'),'sha256':digest(folder/'train-marginals.jsonl.gz'),
             'seconds':round(time.monotonic()-start,1),'TEST_opened':False}
    atomic_json(LOCAL/'cache-summary.json',summary);atomic_json(DEST/'cache-summary.json',summary)
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
