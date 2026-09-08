import gzip
import json
import hashlib
import math
from pathlib import Path
from bootstrap import ROOT
from s06e_p1 import DEFAULT_RANKER
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import require,verify_freeze
from common import Runtime,GlobalSelector
from grammar_p3 import CHANNELS
from s06e_p3 import GrammarNgram
from r5.sequence import BOS,EOS
from analysis_schema_s06e import signature
from evaluate_global import validate_graph

PARENT=DEFAULT_RANKER.parent.parent
DEST=PARENT/'P3-yont-v1'
LOCAL=ROOT/'results_grammar_p3'
HERE=ROOT/'training_controls/grammar_p3'


def records(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt',encoding='utf-8') as f:
        for line in f:yield json.loads(line)


def emit(f,value):f.write(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n')


def close(a,b):
    require(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-9),'P3_SCORE_RECONSTRUCTION:'+str((a,b)))


def original_freeze():
    frozen=read(PARENT/'A2/freeze.json');verify_freeze(PARENT/'A2',frozen)
    outbox=read(ROOT/'results_lexical_p2/github-outbox-final.json')
    require(all(digest(Path(v['local_path']))==v['sha256'] for v in outbox['files'].values()),'P2_PUBLIC_PAYLOAD_CHANGED')
    return {'historical_A2_freeze_sha256':digest(PARENT/'A2/freeze.json'),
            'P2_outbox_sha256':digest(ROOT/'results_lexical_p2/github-outbox-final.json')}


def check_output(rt,raw,out):
    require([(t['raw'],t['start'],t['end'],t['analysis']['analyses']) for t in raw['tokens']]==
            [(t['raw'],t['start'],t['end'],t['analysis']['analyses']) for t in out['tokens']], 'P3_INVENTORY_CHANGED')
    require(Runtime.reconstruct(out)==raw['raw'],'P3_RECONSTRUCTION_FAILED')
    require(all(t['analysis']['search_complete'] for t in out['tokens']),'P3_INCOMPLETE_MORPHOLOGY')
    validate_graph(out);s=rt.context_selector;ts=out['tokens'];theta=dict(zip(CHANNELS,rt.p3_theta))
    ev={e['token']:e for e in out.get('ab04_view_evidence',{}).get('tokens',[])}
    for sol in out['global_solutions']:
        base=GlobalSelector._unaries(s,ts,sol['indices']);total=0.;tags=[BOS,BOS]
        for p in sol['plans']:
            if 'p3_features' in p:
                fs=rt.grammar.plan(ts,p);require(fs==p['p3_features'],'P3_PLAN_FEATURE_CHANGED')
                extra=sum(theta.get(k,0.)*v for k,v in fs.items())
                close(extra,p['p3_score_delta']);close(p['score'],p['p3_base_score']+extra/s.relation_weight)
            total+=s.relation_weight*p['score']
        for i in sol['indices']:
            aid=sol['analysis_bindings'].get(i,sol['analysis_bindings'].get(str(i)))
            if aid is None:
                tags.append(signature('X' if any(c.isalnum() for c in ts[i]['raw']) else 'PUNCT',{}));continue
            a=next(a for a in ts[i]['analysis']['analyses'] if a['analysis_id']==aid)
            total+=base[i][aid]+s.ranker.token(ts,i)[aid]
            if i in ev:total+=ev[i]['effective_weight']*ev[i]['scores'][aid]
            tags.append(rt.grammar.tag(a))
        tags.append(EOS);ng=s.ngram.base if isinstance(s.ngram,GrammarNgram) else s.ngram
        for j in range(2,len(tags)):
            triple=tags[j-2:j+1]
            total+=s.ngram_weight*ng.transition(*(t[:2] for t in triple))
            total+=sum(theta.get(k,0.)*v for k,v in rt.grammar.transition(*triple))
        close(total,sol['score'])
    return len(out['global_solutions'])


def feature_vector(rt,out,block,path,config):
    values={k:0. for k in CHANNELS};tags=[BOS,BOS];s=rt.context_selector
    for i,aid in zip(block,path,strict=True):
        t=out['tokens'][i]
        if not aid:
            tags.append(signature('X' if any(c.isalnum() for c in t['raw']) else 'PUNCT',{}));continue
        a=next(a for a in t['analysis']['analyses'] if a['analysis_id']==aid)
        parts=s.ranker.parts(out['tokens'],i,a)
        values['local_government']+=parts[0];values['local_agreement']+=parts[1]
        tags.append(rt.grammar.tag(a))
    tags.append(EOS)
    for j in range(2,len(tags)):
        for k,v in rt.grammar.transition(*tags[j-2:j+1]):values[k]+=v
    for p in config['plans']:
        for k,v in rt.grammar.plan(out['tokens'],p).items():values[k]+=v
    return [values[k] for k in CHANNELS]
