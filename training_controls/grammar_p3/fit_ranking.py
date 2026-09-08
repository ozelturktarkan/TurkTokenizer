import os
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import copy
import gzip
import hashlib
import json
import time
import sys
from bootstrap import ROOT
sys.path[:0]=[str(ROOT/'.deps-s06'),str(ROOT/'.deps-s05six')]
import numpy as np
from scipy.optimize import minimize
from r5.sequence import decode
from analysis_schema_s06e import signature
from s06e_p3 import Tokenizer,GrammarNgram
from grammar_p3 import CHANNELS,active
from audit_s05_ua_scores import capture_configurations
from .common import ROOT,DEST,LOCAL,HERE,read,records,digest,atomic_json,require,original_freeze,emit,check_output,feature_vector,close


def best(rt,out,block,captured,target,allowed):
    s=rt.context_selector;domains=[];rich=isinstance(s.ngram,GrammarNgram)
    for i in block:
        t=out['tokens'][i]
        domains.append([{'id':a['analysis_id'],'tag':rt.grammar.tag(a) if rich else signature(a['output_pos'],a['features']),
                         'score':captured['unaries'][i][a['analysis_id']]}
                        for a in t['analysis']['analyses'] if i!=target or a['analysis_id'] in allowed] or
                       ([{'id':'','tag':signature('X' if any(c.isalnum() for c in t['raw']) else 'PUNCT',{}),'score':0.}]
                        if not t['analysis']['analyses'] else []))
    def transition(a,b,c):return s.ngram_weight*s.ngram.transition(a,b,c)
    choices=[]
    for config in captured['configs']:
        ds=[[a for a in domain if i not in config['bindings'] or a['id']==config['bindings'][i]] for i,domain in zip(block,domains)]
        found=decode(ds,transition)
        if found is not None:choices.append((found['score']+config['score'],found['path'],config))
    choices.sort(key=lambda x:(-x[0],x[1],json.dumps(x[2]['bindings'],sort_keys=True)))
    return choices[0] if choices else None


def mine(rt,targets,destination,arm,round_index):
    capture_configurations(rt);rows=[];counts={'contexts':0,'targets':0,'missing_retained_contrast':0,'positive_retained_nonnull_plan':0}
    started=time.monotonic()
    with gzip.open(destination,'wt',encoding='utf-8',compresslevel=3) as stream:
        for rec in records(DEST/'train-raw.jsonl.gz'):
            if rec['id'] not in targets:continue
            rt.context_selector.audit_captured.clear();raw=rec['raw_output'];out=rt.analyze_prepared(raw)
            check_output(rt,raw,out);counts['contexts']+=1
            for i in targets[rec['id']]:
                ids={a['analysis_id'] for a in raw['tokens'][i]['analysis']['analyses']}
                positive=set(rec['golds'][i]['positive_analysis_ids']);require(positive and positive<ids,'P3_INVALID_RANK_TARGET')
                sol=next(s for s in out['global_solutions'] if i in s['indices']);block=sol['indices']
                captured=rt.context_selector.audit_captured[tuple(block)]
                p=best(rt,out,block,captured,i,positive);n=best(rt,out,block,captured,i,ids-positive)
                counts['targets']+=1
                if p is None or n is None:counts['missing_retained_contrast']+=1;continue
                close(max(p[0],n[0]),sol['score'])
                pf=feature_vector(rt,out,block,p[1],p[2]);nf=feature_vector(rt,out,block,n[1],n[2])
                x=[a-b for a,b in zip(pf,nf)];gap=p[0]-n[0]
                constant=gap-sum(a*b for a,b in zip(rt.p3_theta,x))
                counts['positive_retained_nonnull_plan']+=bool(p[2]['plans'])
                row={'context_id':rec['id'],'token':i,'x':x,'constant':constant,'gap':gap,
                     'preferred_positive':gap>=0,'positive_id':p[1][block.index(i)],'negative_id':n[1][block.index(i)],
                     'retained_configurations':len(captured['configs'])}
                rows.append(row);emit(stream,row)
            if counts['contexts']%20==0 or counts['contexts']==len(targets):
                print(json.dumps({'stage':'P3_A3_MINE','arm':arm,'round':round_index,**counts,'seconds':round(time.monotonic()-started,1)}),flush=True)
            rt.grammar.transition.cache_clear()
            if isinstance(rt.context_selector.ngram,GrammarNgram):rt.context_selector.ngram.transition.cache_clear()
    require(counts['contexts']==len(targets),'P3_MISSING_TRAIN_CONTEXT')
    return rows,counts


def fit(rows,arm,prior,cfg):
    ids=[i for i,k in enumerate(CHANNELS) if active(k,arm)]
    require(bool(rows),'P3_NO_RANKING_CONTRASTS')
    X=np.asarray([r['x'] for r in rows])[:,ids];constant=np.asarray([r['constant'] for r in rows]);center=np.asarray(prior)[ids]
    def fun(w):
        error=np.maximum(0.,cfg['margin']-constant-X@w)
        reg=cfg['regularization'];delta=w-center
        return float(np.mean(error**2)+reg*np.dot(delta,delta)), -2.*X.T@error/len(rows)+2*reg*delta
    bounds=[tuple(cfg['local_scale_bounds'] if i<2 else cfg['grammar_weight_bounds']) for i in ids]
    result=minimize(fun,center,jac=True,method='L-BFGS-B',bounds=bounds,options={'maxiter':100,'ftol':1e-10})
    require(np.isfinite(result.x).all(),'P3_A3_NONFINITE')
    require(result.fun<=fun(center)[0]+1e-9,'P3_A3_LOSS_INCREASED')
    theta=[0.]*len(CHANNELS)
    for i,v in zip(ids,result.x):theta[i]=float(v)
    return theta,{'initial_loss':fun(center)[0],'final_loss':float(result.fun),'optimizer_success':bool(result.success),
                  'optimizer_message':str(result.message),'iterations':int(result.nit),'contrasts':len(rows)}


def main():
    require(not (DEST/'ranking').exists(),'P3_REFUSE_OVERWRITE_RANKING')
    (DEST/'ranking').mkdir();model=read(DEST/'local-model.json');cfg=read(HERE/'protocol.json')['A3']
    require(digest(DEST/'local-model.json')==read(LOCAL/'local-fit-summary.json')['model_sha256'],'P3_LOCAL_MODEL_CHANGED')
    prep=read(LOCAL/'prepare-summary.json')
    require(digest(DEST/'train-raw.jsonl.gz')==prep['artifacts']['train-raw.jsonl.gz'],'P3_TRAIN_RAW_CHANGED')
    candidates=[]
    for rec in records(DEST/'train-raw.jsonl.gz'):
        if rec['eligible_targets']:
            key=lambda i:hashlib.sha256((rec['id']+':'+str(i)).encode()).hexdigest()
            candidates.append((rec['id'],sorted(rec['eligible_targets'],key=key)[:cfg['targets_per_context']]))
    candidates.sort(key=lambda r:hashlib.sha256(r[0].encode()).hexdigest())
    targets=dict(candidates[:cfg['train_contexts']]);require(len(targets)==cfg['train_contexts'],'P3_TOO_FEW_CONTEXTS')
    atomic_json(DEST/'ranking/targets.json',targets)
    frozen={**read(LOCAL/'prepare-freeze.json')['source_sha256'],**{n:digest(ROOT/n) for n in [
        'training_controls/grammar_p3/fit_local.py','training_controls/grammar_p3/fit_ranking.py','training_controls/grammar_p3/validate.py']}}
    atomic_json(LOCAL/'ranking-freeze.json',frozen);history={};configs={'C0_P2':{'arm':'combined','theta':[0.]*len(CHANNELS)}}
    for arm,name in [('government','GOV'),('agreement','AGR'),('combined','JOINT_FULL')]:
        theta=[0.]*len(CHANNELS)
        for i in range(2):theta[i]=float(active(CHANNELS[i],arm))
        prior=list(theta);history[arm]=[]
        for r in range(2):
            rt=Tokenizer(model=model,theta=theta,arm=arm,configuration='TRAIN_'+arm)
            rows,counts=mine(rt,targets,DEST/f'ranking/{arm}-round-{r}.jsonl.gz',arm,r)
            new,fitresult=fit(rows,arm,prior,cfg)
            record={'round':r,'mining':counts,'fit':fitresult,'theta_before':theta,'theta_after':new}
            theta=new;history[arm].append(record)
            atomic_json(LOCAL/'ranking-progress.json',history)
            print(json.dumps({'stage':'P3_A3_FIT','arm':arm,'round':r,**fitresult}),flush=True)
            del rt
        configs[name]={'arm':arm,'theta':theta}
    configs['LOCAL_COMBINED']={'arm':'combined','theta':[1.,1.]+[0.]*(len(CHANNELS)-2)}
    configs['JOINT_HALF']={'arm':'combined','theta':[.5*x for x in configs['JOINT_FULL']['theta']]}
    model['configurations']=configs;model['channels']=list(CHANNELS)
    model['source_sha256']=frozen;model['training_targets_sha256']=digest(DEST/'ranking/targets.json')
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P3_RANK_SOURCE_CHANGED');original_freeze()
    atomic_json(DEST/'model.json',model)
    atomic_json(LOCAL/'model-location.json',{'path':str(DEST/'model.json'),'sha256':digest(DEST/'model.json')})
    summary={'status':'A3_RANKING_COMPLETE','TRAIN_contexts':len(targets),'TRAIN_targets':sum(map(len,targets.values())),
             'rounds_per_arm':2,'history':history,'model_sha256':digest(DEST/'model.json'),'TEST_opened':False}
    atomic_json(LOCAL/'ranking-summary.json',summary);atomic_json(DEST/'ranking-summary.json',summary)
    print(json.dumps({'status':summary['status'],'model_sha256':summary['model_sha256']}),flush=True)


if __name__=='__main__':main()
