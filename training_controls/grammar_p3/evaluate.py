"""Six registered DEV arms; seal one choice before a single CALIB comparison."""
import os
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import copy
import gzip
import json
import time
from s06e_p3 import Tokenizer,Codec,GrammarNgram
from a123_measurement import measure,summarize
from training_controls.phonology_p1.evaluate import inventory
from training_controls.lexical_p2.evaluate import projection_rows,view_summary
from .common import ROOT,PARENT,DEST,LOCAL,HERE,read,records,digest,atomic_json,require,original_freeze,emit,check_output
from .validate import PROBES,run as probes

BASE=PARENT/'P2-lexical-v1/policy-imst/evaluation/1.00'


def safe(result,baseline):
    r,b=result['legacy'],baseline['legacy']
    return (r['preferred_lemma_pos']>=b['preferred_lemma_pos'] and
            r['preferred_declared_features']>=b['preferred_declared_features'] and
            r['legacy_selected_lemma_wrong']<=b['legacy_selected_lemma_wrong'] and
            result['views']['predicted_view_lemma_pos']>=baseline['views']['predicted_view_lemma_pos'])


def paired(old,new):
    require([(r['id'],r['start'],r['end']) for r in old]==[(r['id'],r['start'],r['end']) for r in new],'P3_PAIRED_ALIGNMENT')
    keys=('preferred_lemma_pos','preferred_declared_features') if 'preferred_lemma_pos' in old[0] else ('predicted_view_lemma_pos','predicted_view_features')
    return {k:{'fixed':sum(not a[k] and b[k] for a,b in zip(old,new)),
               'regressed':sum(a[k] and not b[k] for a,b in zip(old,new))} for k in keys}


def clear(rt):
    rt.grammar.transition.cache_clear()
    def visit(s):
        if isinstance(s.ngram,GrammarNgram):s.ngram.transition.cache_clear()
        for attr in ('reference_selector','reference_ua'):
            child=getattr(s,attr,None)
            if child is not None:visit(child)
    visit(rt.context_selector);rt.head.views.cache.clear()


def main():
    require(not (DEST/'evaluation').exists(),'P3_REFUSE_OVERWRITE_EVALUATION')
    original_freeze();cfg=read(HERE/'protocol.json');modelmeta=read(LOCAL/'model-location.json')
    require(digest(DEST/'model.json')==modelmeta['sha256'],'P3_MODEL_CHANGED')
    model=read(DEST/'model.json');frozen={**read(LOCAL/'ranking-freeze.json'),str((HERE/'evaluate.py').relative_to(ROOT)).replace('\\','/'):digest(HERE/'evaluate.py')}
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P3_EVALUATION_SOURCE_CHANGED')
    manifests=read(ROOT/'training/a1-large-v1/manifest.json')['files']
    references={split:digest(ROOT/f'training/a1-large-v1/{split}.jsonl') for split in ('dev','calib')}
    require(all(h==manifests[split+'.jsonl'] for split,h in references.items()),'P3_REFERENCE_CHANGED')
    atomic_json(LOCAL/'evaluation-freeze.json',{'source_sha256':frozen,'reference_sha256':references,'model_sha256':modelmeta['sha256']})
    (DEST/'evaluation').mkdir();results={};details={};start=time.monotonic()
    previous=read(ROOT/'results_lexical_p2/policy-imst/comparison.json')['arms']['1.00']
    def baseline(split):
        expected=previous[split]
        require(all(digest(BASE/split/n)==h for n,h in expected['artifact_sha256'].items()),'P3_BASELINE_ARTIFACT_CHANGED')
        native=list(records(BASE/split/'native-words.jsonl.gz'));views=list(records(BASE/split/'view-words.jsonl.gz'))
        require(summarize(native)==expected['legacy'] and view_summary(views)==expected['views'],'P3_BASELINE_SUMMARY_CHANGED')
        details[('C0_P2',split)]=(native,views)
        result={**copy.deepcopy(expected),'configuration':'C0_P2','control_reused_verified_P2':True,
                'objective_blocks_verified_this_run':0,'output_path':str(BASE/split/'outputs.jsonl.gz')}
        results.setdefault('C0_P2',{})[split]=result
        return result
    def run(name,split):
        print(json.dumps({'stage':'P3_EVAL_LOAD','configuration':name,'split':split}),flush=True)
        rt=Tokenizer(name);codec=Codec(name);codec.native=rt
        folder=DEST/'evaluation'/name/split;folder.mkdir(parents=True)
        native=[];views=[];blocks=0
        refs=list(records(ROOT/f'training/a1-large-v1/{split}.jsonl'))
        with gzip.open(folder/'outputs.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as stream:
            for n,(ref,previous_out) in enumerate(zip(refs,records(BASE/split/'outputs.jsonl.gz'),strict=True),1):
                require(ref['id']==previous_out['id'],'P3_BASELINE_ID_MISMATCH')
                raw=rt._raw_schema_sentence(ref['text']);require(inventory(raw)==inventory(previous_out['output']),'P3_CANDIDATE_DRIFT')
                out=rt.analyze_prepared(raw);blocks+=check_output(rt,raw,out)
                native.extend(measure(ref,out));views.extend(projection_rows(ref,out,rt.head.views))
                require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==ref['text'],'P3_BPE_ROUNDTRIP')
                emit(stream,{'id':ref['id'],'output':out})
                clear(rt)
                if n%25==0 or n==len(refs):
                    print(json.dumps({'stage':'P3_EVALUATION','configuration':name,'split':split,'sentences':n,'total':len(refs),'seconds':round(time.monotonic()-start,1)}),flush=True)
        require(len(native)==(4070 if split=='dev' else 2266),'P3_DENOMINATOR_CHANGED')
        for name_,rows in [('native-words',native),('view-words',views)]:
            with gzip.open(folder/(name_+'.jsonl.gz'),'wt',encoding='utf-8') as f:
                for row in rows:emit(f,row)
        oldn,oldv=details[('C0_P2',split)]
        result={'configuration':name,'legacy':summarize(native),'views':view_summary(views),
                'paired':{**paired(oldn,native),**paired(oldv,views)},
                'changed_native_analysis_ids':sum(a['native_analysis_id']!=b['native_analysis_id'] for a,b in zip(oldv,views)),
                'objective_blocks_verified_this_run':blocks,'BPE_roundtrips':len(refs),'output_path':str(folder/'outputs.jsonl.gz'),
                'artifact_sha256':{p.name:digest(p) for p in folder.iterdir() if p.is_file()}}
        require(all(result['legacy'][k]==results['C0_P2'][split]['legacy'][k] for k in ('candidate_lemma_pos','candidate_declared_features')),'P3_NATIVE_COVERAGE_DRIFT')
        require(all(result['views'][k]==results['C0_P2'][split]['views'][k] for k in ('oracle_view_lemma_pos','oracle_view_features')),'P3_VIEW_COVERAGE_DRIFT')
        result['P2_nonregression']=safe(result,results['C0_P2'][split])
        details[(name,split)]=(native,views);results.setdefault(name,{})[split]=result
        atomic_json(folder/'summary.json',result);atomic_json(LOCAL/'evaluation-progress.json',results)
        print(json.dumps({'stage':'P3_SPLIT_COMPLETE','configuration':name,'split':split,'legacy':result['legacy'],'views':result['views'],'P2_nonregression':result['P2_nonregression']}),flush=True)
        clear(rt)
    baseline('dev')
    for name in cfg['DEV_arms']:
        if name!='C0_P2':run(name,'dev')
    eligible=[name for name in cfg['DEV_arms'] if safe(results[name]['dev'],results['C0_P2']['dev'])]
    def key(name):
        r=results[name]['dev'];theta=model['configurations'][name]['theta']
        return (r['views']['predicted_view_lemma_pos'],r['views']['predicted_view_features'],r['legacy']['preferred_lemma_pos'],
                -sum(bool(x) for x in theta),-sum(abs(x) for x in theta),-cfg['DEV_arms'].index(name))
    selected=max(eligible,key=key)
    seal={'configuration':selected,'eligible_arms':eligible,'selected_on':'DEV_ONLY','CALIB_started':False,
          'model_sha256':modelmeta['sha256'],'evaluation_freeze_sha256':digest(LOCAL/'evaluation-freeze.json'),'DEV_results':results}
    atomic_json(LOCAL/'dev-selection-seal.json',seal);atomic_json(DEST/'dev-selection-seal.json',seal)
    baseline('calib')
    if selected!='C0_P2':run(selected,'calib')
    calib_safe=safe(results[selected]['calib'],results['C0_P2']['calib'])
    final_configuration=selected if calib_safe else 'C0_P2'
    diagnostic={}
    for name in dict.fromkeys(['C0_P2',selected]):
        rt=Tokenizer(name);codec=Codec(name);codec.native=rt
        diagnostic[name]=probes(rt,codec,PROBES);clear(rt)
    atomic_json(LOCAL/'postfit-probes.json',{'scope':'AUTHORED_DIAGNOSTIC_NOT_INDEPENDENT_TEST','arms':diagnostic,'selection_changed_by_probes':False})
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P3_EVALUATED_SOURCE_CHANGED');original_freeze()
    final={'status':'EXPERIMENT_COMPLETE','arms':results,'DEV_selected':selected,'CALIB_nonregression':calib_safe,
           'retained_configuration':final_configuration,'default_promoted':False,'TEST_opened':False,
           'model_sha256':modelmeta['sha256'],'new_morphological_paths':False,'BPE_IDs_preserved':224309,
           'candidate_inventory_identical':True,'seconds':round(time.monotonic()-start,1)}
    atomic_json(DEST/'comparison.json',final);atomic_json(LOCAL/'comparison.json',final)
    print(json.dumps({'stage':'P3_EVALUATION_COMPLETE','DEV_selected':selected,'CALIB_nonregression':calib_safe,'retained_configuration':final_configuration}),flush=True)


if __name__=='__main__':main()
