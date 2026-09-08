"""Full decoder checks for separate ranking and combined-layer variants."""
import copy
import gzip
import json
import time
from pathlib import Path
from s06e_p4 import Tokenizer,Codec
from a123_measurement import measure,summarize
from training_controls.phonology_p1.evaluate import inventory
from training_controls.lexical_p2.evaluate import projection_rows,view_summary
from training_controls.grammar_p3.evaluate import paired
from .common import ROOT,DEST,LOCAL,HERE,BASE,read,records,digest,atomic_json,require,original_freeze,emit,check_output


def safe(r,b):
    return (all(r['legacy'][k]>=b['legacy'][k] for k in ('preferred_lemma_pos','preferred_declared_features')) and
            r['legacy']['legacy_selected_lemma_wrong']<=b['legacy']['legacy_selected_lemma_wrong'] and
            all(r['views'][k]>=b['views'][k] for k in ('predicted_view_lemma_pos','predicted_view_features')))


def main():
    folder=DEST/'evaluation';require(not folder.exists(),'P4_REFUSE_OVERWRITE_EVALUATION');folder.mkdir()
    meta=read(LOCAL/'model-location.json');model=read(DEST/'model.json');require(digest(DEST/'model.json')==meta['sha256'],'P4_EVAL_MODEL_CHANGED')
    frozen={**read(LOCAL/'rank-freeze.json'),str((HERE/'evaluate.py').relative_to(ROOT)).replace('\\','/'):digest(HERE/'evaluate.py')}
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_EVAL_SOURCE_CHANGED')
    manifests=read(ROOT/'training/a1-large-v1/manifest.json')['files']
    references={s:digest(ROOT/f'training/a1-large-v1/{s}.jsonl') for s in ('dev','calib')}
    require(all(h==manifests[s+'.jsonl'] for s,h in references.items()),'P4_EVAL_REFERENCE_CHANGED')
    atomic_json(LOCAL/'evaluation-freeze.json',{'source_sha256':frozen,'references':references,'model_sha256':meta['sha256']})
    hs=model['selected_head_strength'];configs={'P2':{'head_strength':0.,'rank_strength':0.,'rank_variant':'base_head'}}
    if hs:configs['H']={'head_strength':hs,'rank_strength':0.,'rank_variant':'selected_head'}
    for variant,prefix,h in [('base_head','R',0.),('selected_head','HR',hs)]:
        if prefix=='HR' and hs==0:continue
        for s in read(HERE/'protocol.json')['rank']['strengths']:
            configs[f'{prefix}_{s:.2f}']={'head_strength':h,'rank_strength':s,'rank_variant':variant}
    original=read(ROOT/'results_lexical_p2/policy-imst/comparison.json')['arms']['1.00'];results={};details={};start=time.monotonic()
    def control(split):
        b=original[split];require(all(digest(BASE/split/n)==h for n,h in b['artifact_sha256'].items()),'P4_BASELINE_CHANGED')
        native=list(records(BASE/split/'native-words.jsonl.gz'));view=list(records(BASE/split/'view-words.jsonl.gz'))
        require(summarize(native)==b['legacy'] and view_summary(view)==b['views'],'P4_BASELINE_COUNTS_CHANGED')
        details[('P2',split)]=(native,view)
        results.setdefault('P2',{})[split]={**copy.deepcopy(b),'configuration':configs['P2'],'verified_P2_control_reused':True,
            'objective_blocks_verified_this_run':0,'output_path':str(BASE/split/'outputs.jsonl.gz')}
    def run(name,split):
        args=configs[name];dest=folder/name/split;dest.mkdir(parents=True);rt=Tokenizer(**args);codec=Codec(**args);codec.native=rt
        native=[];view=[];blocks=0;refs=list(records(ROOT/f'training/a1-large-v1/{split}.jsonl'))
        print(json.dumps({'stage':'P4_EVAL_LOAD','configuration':name,'split':split}),flush=True)
        with gzip.open(dest/'outputs.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as f:
            for n,(ref,rec) in enumerate(zip(refs,records(BASE/split/'outputs.jsonl.gz'),strict=True),1):
                require(ref['id']==rec['id'],'P4_EVAL_ID_MISMATCH')
                if not args['rank_strength']:
                    out=rt._finish(copy.deepcopy(rec['output']))
                    require(out['global_solutions']==rec['output']['global_solutions'],'P4_H_CHANGED_NATIVE_SCORE')
                    require(measure(ref,out)==measure(ref,rec['output']),'P4_H_CHANGED_NATIVE_RESULT')
                else:
                    raw=rt._raw_schema_sentence(ref['text']);require(inventory(raw)==inventory(rec['output']),'P4_NATIVE_CANDIDATE_DRIFT')
                    out=rt.analyze_prepared(raw);blocks+=check_output(rt,raw,out)
                native.extend(measure(ref,out));view.extend(projection_rows(ref,out,rt.head.views))
                require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==ref['text'],'P4_BPE_ROUNDTRIP')
                emit(f,{'id':ref['id'],'output':out})
                if n%50==0 or n==len(refs):print(json.dumps({'stage':'P4_EVALUATION','configuration':name,'split':split,'sentences':n,'total':len(refs),'seconds':round(time.monotonic()-start,1)}),flush=True)
                if n%100==0:rt.head.views.cache.clear()
        require(len(native)==(4070 if split=='dev' else 2266),'P4_EVAL_DENOMINATOR')
        for name_,rows in [('native-words',native),('view-words',view)]:
            with gzip.open(dest/(name_+'.jsonl.gz'),'wt',encoding='utf-8') as stream:
                for row in rows:emit(stream,row)
        oldn,oldv=details[('P2',split)];b=results['P2'][split]
        result={'configuration':args,'legacy':summarize(native),'views':view_summary(view),'paired':{**paired(oldn,native),**paired(oldv,view)},
                'changed_native_analysis_ids':sum(a['native_analysis_id']!=b_['native_analysis_id'] for a,b_ in zip(oldv,view)),
                'objective_blocks_verified_this_run':blocks,'BPE_roundtrips':len(refs),'output_path':str(dest/'outputs.jsonl.gz'),
                'artifact_sha256':{p.name:digest(p) for p in dest.iterdir() if p.is_file()}}
        require(all(result['legacy'][k]==b['legacy'][k] for k in ('candidate_lemma_pos','candidate_declared_features')),'P4_NATIVE_COVERAGE_CHANGED')
        require(all(result['views'][k]==b['views'][k] for k in ('oracle_view_lemma_pos','oracle_view_features')),'P4_VIEW_COVERAGE_CHANGED')
        result['P2_nonregression']=safe(result,b);results.setdefault(name,{})[split]=result;details[(name,split)]=(native,view)
        atomic_json(dest/'summary.json',result);atomic_json(LOCAL/'evaluation-progress.json',results)
        print(json.dumps({'stage':'P4_SPLIT_COMPLETE','configuration':name,'split':split,'legacy':result['legacy'],'views':result['views'],'P2_nonregression':result['P2_nonregression']}),flush=True)
    control('dev')
    for name in configs:
        if name!='P2':run(name,'dev')
    def key(name):
        r=results[name]['dev'];c=configs[name]
        return (r['views']['predicted_view_lemma_pos'],r['views']['predicted_view_features'],r['legacy']['preferred_lemma_pos'],
                -(bool(c['head_strength'])+bool(c['rank_strength'])),-c['rank_strength'],-c['head_strength'])
    eligible=[n for n in configs if safe(results[n]['dev'],results['P2']['dev'])];selected=max(eligible,key=key)
    seal={'name':selected,'configuration':configs[selected],'eligible':eligible,'selected_on':'DEV_ONLY','CALIB_started':False,
          'model_sha256':meta['sha256'],'DEV_results':results,'configs':configs}
    atomic_json(LOCAL/'dev-selection-seal.json',seal);atomic_json(DEST/'dev-selection-seal.json',seal)
    control('calib')
    if selected!='P2':run(selected,'calib')
    accepted=safe(results[selected]['calib'],results['P2']['calib']);retained=selected if accepted else 'P2'
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_EVALUATED_SOURCE_CHANGED');original_freeze()
    summary={'status':'EXPERIMENT_COMPLETE','arms':results,'configs':configs,'DEV_selected':selected,'CALIB_nonregression':accepted,
             'retained':retained,'model_sha256':meta['sha256'],'default_promoted':False,'TEST_opened':False,
             'ordered_candidates_unchanged':True,'BPE_IDs_preserved':224309,'seconds':round(time.monotonic()-start,1)}
    atomic_json(LOCAL/'comparison.json',summary);atomic_json(DEST/'comparison.json',summary)
    print(json.dumps({'stage':'P4_EVALUATION_COMPLETE','DEV_selected':selected,'retained':retained,'CALIB_nonregression':accepted}),flush=True)


if __name__=='__main__':main()
