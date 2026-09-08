"""Frozen references, DEV-only selection, then a sealed CALIB check."""
import os
for var in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[var]='1'
import copy
import gzip
import json
import time
from pathlib import Path

from bootstrap import ROOT
from s06e_p2 import Tokenizer
from s06e_p2bpe import Tokenizer as Codec
from s06e_r5bpe import Tokenizer as OldCodec
from analysis_schema_p2 import view_matches
from a123_measurement import measure,summarize
from training_controls.phonology_p1.evaluate import inventory
from training_controls.a3_epoch.train import check_output
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import verify_freeze,require
from .fit import DEST,LOCAL,PARENT,HERE


def records(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt',encoding='utf-8') as f:
        for line in f: yield json.loads(line)


def projection_rows(ref,out,views):
    spans={(t['start'],t['end']):t for t in out['tokens']}; rows=[]
    for u in ref['units']:
        if u['punctuation']: continue
        t=spans.get((u['start'],u['end'])); gold=u['gold']
        aa=t['analysis']['analyses'] if t else []
        p=t.get('context_decision',{}).get('preferred_analysis') if t else None
        v=t['lexical_decision']['preferred_view'] if t else None
        vv=[(a,x) for a in aa for x in views.options(a)]
        cop=u['projection']=='EXPLICIT_SOURCE_NOMINAL_COPULA'
        rows.append({'id':ref['id'],'start':u['start'],'end':u['end'],'surface':u['form'],
            'oracle_view_lemma_pos':any(view_matches(x,gold) for _,x in vv),
            'oracle_view_features':any(view_matches(x,gold,True,cop,a) for a,x in vv),
            'predicted_view_lemma_pos':bool(v and view_matches(v,gold)),
            'predicted_view_features':bool(v and view_matches(v,gold,True,cop,p)),
            'native_analysis_id':p['analysis_id'] if p else None,'predicted_view':v,'gold':gold})
    return rows


def view_summary(rows):
    keys=('oracle_view_lemma_pos','oracle_view_features','predicted_view_lemma_pos','predicted_view_features')
    return {**{k:sum(r[k] for r in rows) for k in keys},'words':len(rows)}


def main():
    require(not (DEST/'evaluation').exists(),'P2_EVAL_REFUSE_OVERWRITE')
    require(read(LOCAL/'fit-summary.json')['status']=='FIT_COMPLETE','P2_FIT_INCOMPLETE')
    frozen_fit=read(LOCAL/'freeze.json')
    require(all(digest(ROOT/n)==h for n,h in frozen_fit['sources'].items()),'P2_FITTED_SCHEMA_CHANGED')
    oldfreeze=read(PARENT/'A2/freeze.json'); verify_freeze(PARENT/'A2',oldfreeze)
    config=read(HERE/'protocol.json')
    files=['s06e_p2.py','s06e_p2bpe.py','analysis_schema_p2.py']+[str(p.relative_to(ROOT)).replace('\\','/') for p in HERE.iterdir() if p.suffix in {'.py','.json'}]
    frozen={n:digest(ROOT/n) for n in files}
    atomic_json(LOCAL/'evaluation-freeze.json',frozen)
    atomic_json(DEST/'evaluation-freeze.json',frozen)
    base=PARENT/'P1-phonology-v1'; old=OldCodec(); results={}; detailed={}; start=time.monotonic()
    (DEST/'evaluation').mkdir()
    def run(strength,split):
        key=f'{strength:.2f}'; folder=DEST/'evaluation'/key/split; folder.mkdir(parents=True)
        print(json.dumps({'stage':'LOAD','strength':strength,'split':split}),flush=True)
        rt=Tokenizer(strength); codec=Codec(strength); codec.native=rt
        require(codec.entries==old.entries and codec.surfaces==old.surfaces and codec.lookup==old.lookup,'P2_ID_DRIFT')
        refs=list(records(ROOT/f'training/a1-large-v1/{split}.jsonl'))
        baseline=list(records(base/'combined'/split/'outputs.jsonl.gz'))
        native=[]; projected=[]; blocks=0
        with gzip.open(folder/'outputs.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as stream:
            for n,(ref,b) in enumerate(zip(refs,baseline,strict=True),1):
                require(ref['id']==b['id'],'P2_REFERENCE_ID_MISMATCH')
                raw=rt._raw_schema_sentence(ref['text'])
                require(inventory(raw)==inventory(b['output']),'P2_CANDIDATE_DRIFT')
                out=rt.analyze_prepared(raw); blocks+=check_output(rt,raw,out)
                rows=measure(ref,out); native.extend(rows)
                projected.extend(projection_rows(ref,out,rt.head.views))
                require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==ref['text'],'P2_BPE_ROUNDTRIP')
                if strength==0:
                    require(rows==measure(ref,b['output']),'P2_ZERO_RESIDUAL_NOT_P1')
                stream.write(json.dumps({'id':ref['id'],'output':out},ensure_ascii=False)+'\n')
                if n%50==0 or n==len(refs):
                    print(json.dumps({'stage':'DECODER','strength':strength,'split':split,'sentences':n,'total':len(refs),'seconds':round(time.monotonic()-start,1)}),flush=True)
        require(len(native)==(4070 if split=='dev' else 2266),'P2_DENOMINATOR')
        for name,rows in [('native-words',native),('view-words',projected)]:
            with gzip.open(folder/(name+'.jsonl.gz'),'wt',encoding='utf-8') as f:
                for row in rows: f.write(json.dumps(row,ensure_ascii=False)+'\n')
        result={'legacy':summarize(native),'views':view_summary(projected),'objective_blocks_verified':blocks,
                'BPE_roundtrips':len(refs),'strength':strength,
                'artifact_sha256':{p.name:digest(p) for p in folder.iterdir() if p.is_file()}}
        if strength!=0:
            oldn,oldv=detailed[('0.00',split)]
            result['paired']={}
            for name,a,b in [('legacy_lemma_pos',[r['preferred_lemma_pos'] for r in oldn],[r['preferred_lemma_pos'] for r in native]),
                  ('legacy_features',[r['preferred_declared_features'] for r in oldn],[r['preferred_declared_features'] for r in native]),
                  ('projected_lemma_pos',[r['predicted_view_lemma_pos'] for r in oldv],[r['predicted_view_lemma_pos'] for r in projected]),
                  ('projected_features',[r['predicted_view_features'] for r in oldv],[r['predicted_view_features'] for r in projected])]:
                result['paired'][name]={'fixed':sum(not x and y for x,y in zip(a,b)), 'regressed':sum(x and not y for x,y in zip(a,b))}
            result['changed_native_analysis_ids']=sum(a['native_analysis_id']!=b['native_analysis_id'] for a,b in zip(oldv,projected))
        detailed[(key,split)]=(native,projected)
        results.setdefault(key,{})[split]=result
        atomic_json(folder/'summary.json',result)
        atomic_json(LOCAL/'progress-summary.json',results)
        print(json.dumps({'stage':'SPLIT_COMPLETE','strength':strength,'split':split,'legacy':result['legacy'],'views':result['views']},ensure_ascii=False),flush=True)
    for strength in config['dev_arms']: run(strength,'dev')
    control=results['0.00']['dev']['legacy']
    qualified=[s for s in config['dev_arms'] if results[f'{s:.2f}']['dev']['legacy']['preferred_lemma_pos']>=control['preferred_lemma_pos']
               and results[f'{s:.2f}']['dev']['legacy']['preferred_declared_features']>=control['preferred_declared_features']]
    selected=max(qualified,key=lambda s:(results[f'{s:.2f}']['dev']['legacy']['preferred_lemma_pos'],
        results[f'{s:.2f}']['dev']['views']['predicted_view_features'],-s))
    seal={'strength':selected,'selected_on':'DEV_ONLY','DEV_complete':True,'CALIB_started':False,
          'head_sha256':read(LOCAL/'model-location.json')['sha256'],'source_sha256':frozen}
    atomic_json(LOCAL/'dev-selection-seal.json',seal); atomic_json(DEST/'dev-selection-seal.json',seal)
    run(0.,'calib')
    if selected!=0: run(selected,'calib')
    verify_freeze(PARENT/'A2',oldfreeze)
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P2_EVALUATED_SOURCE_CHANGED')
    chosen=results[f'{selected:.2f}']
    historical=read(ROOT/'results_phonology_p1/comparison.json')['arms']['baseline']
    safe=all(chosen[s]['legacy']['preferred_lemma_pos']>=historical[s]['counts']['preferred_lemma_pos'] and
        chosen[s]['legacy']['preferred_declared_features']>=historical[s]['counts']['preferred_declared_features'] and
        chosen[s]['legacy']['legacy_selected_lemma_wrong']<=historical[s]['counts']['legacy_selected_lemma_wrong'] for s in ('dev','calib'))
    final={'status':'EXPERIMENT_COMPLETE','arms':results,'selected_strength':selected,'historical_E05_nonregression':safe,
           'default_promoted':False,'selected_on':'DEV_ONLY','TEST_opened':False,'new_morphological_paths':False,
           'BPE_IDs_preserved':224309,'historical_freeze_verified':True,'seconds':round(time.monotonic()-start,1)}
    atomic_json(DEST/'comparison.json',final); atomic_json(LOCAL/'comparison.json',final)
    print(json.dumps({'stage':'COMPLETE','selected_strength':selected,'historical_E05_nonregression':safe}),flush=True)


if __name__=='__main__': main()
