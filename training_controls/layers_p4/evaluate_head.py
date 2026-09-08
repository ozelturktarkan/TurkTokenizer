"""DEV-only conditional view head choice with all native decisions fixed."""
import copy
import gzip
import json
import time
from s06e_p4 import Tokenizer,Codec
from a123_measurement import measure,summarize
from training_controls.lexical_p2.evaluate import projection_rows,view_summary
from training_controls.grammar_p3.evaluate import paired
from .common import ROOT,DEST,LOCAL,HERE,BASE,read,records,digest,atomic_json,require,original_freeze,emit


def main():
    folder=DEST/'head/evaluation';require(not folder.exists(),'P4_REFUSE_OVERWRITE_HEAD_EVAL');folder.mkdir()
    model=read(DEST/'head-model.json');require(digest(DEST/'head-model.json')==read(LOCAL/'head-fit-summary.json')['model_sha256'],'P4_HEAD_MODEL_CHANGED')
    frozen=read(LOCAL/'head-freeze.json');require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_HEAD_FEATURE_SOURCE_CHANGED')
    source=HERE/'evaluate_head.py';atomic_json(LOCAL/'head-evaluation-freeze.json',{'sources':frozen,'evaluation_source_sha256':digest(source)})
    config=read(HERE/'protocol.json')['head'];base=read(ROOT/'results_lexical_p2/policy-imst/comparison.json')['arms']['1.00']['dev']
    require(all(digest(BASE/'dev'/n)==h for n,h in base['artifact_sha256'].items()),'P4_HEAD_BASELINE_CHANGED')
    oldn=list(records(BASE/'dev/native-words.jsonl.gz'));oldv=list(records(BASE/'dev/view-words.jsonl.gz'))
    refs=list(records(ROOT/'training/a1-large-v1/dev.jsonl'));results={'0.00':{'legacy':base['legacy'],'views':base['views'],'verified_P2_control_reused':True}}
    start=time.monotonic()
    for strength in config['strengths']:
        if strength==0:continue
        key=f'{strength:.2f}';dest=folder/key;dest.mkdir();rt=Tokenizer(model=model,head_strength=strength);codec=Codec(model=model,head_strength=strength);codec.native=rt
        rows=[]
        with gzip.open(dest/'outputs.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as stream:
            for n,(ref,rec) in enumerate(zip(refs,records(BASE/'dev/outputs.jsonl.gz'),strict=True),1):
                require(ref['id']==rec['id'],'P4_HEAD_REF_ALIGNMENT');old=rec['output'];out=rt._finish(copy.deepcopy(old))
                require(old['global_solutions']==out['global_solutions'],'P4_HEAD_CHANGED_NATIVE_SOLUTIONS')
                require([t.get('context_decision') for t in old['tokens']]==[t.get('context_decision') for t in out['tokens']],'P4_HEAD_CHANGED_NATIVE_DECISIONS')
                require([t.get('decision_layers') for t in old['tokens']]==[t.get('decision_layers') for t in out['tokens']],'P4_HEAD_CHANGED_NATIVE_CONFIDENCE')
                require(measure(ref,old)==measure(ref,out),'P4_HEAD_CHANGED_NATIVE_METRICS')
                require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==ref['text'],'P4_HEAD_BPE_ROUNDTRIP')
                rows.extend(projection_rows(ref,out,rt.head.views));emit(stream,{'id':ref['id'],'output':out})
                if n%75==0 or n==len(refs):print(json.dumps({'stage':'P4_HEAD_DEV','strength':strength,'sentences':n,'total':len(refs),'seconds':round(time.monotonic()-start,1)}),flush=True)
        result={'head_strength':strength,'legacy':base['legacy'],'views':view_summary(rows),'paired':paired(oldv,rows),
                'native_choices_scores_and_confidence_unchanged':True,'BPE_roundtrips':len(refs),'output_sha256':digest(dest/'outputs.jsonl.gz')}
        results[key]=result;atomic_json(dest/'summary.json',result);atomic_json(LOCAL/'head-progress.json',results)
        print(json.dumps({'stage':'P4_HEAD_DEV_COMPLETE','strength':strength,'views':result['views'],'paired':result['paired']}),flush=True)
    qualifies=[s for s in config['strengths'] if all(results[f'{s:.2f}']['views'][k]>=base['views'][k] for k in ('predicted_view_lemma_pos','predicted_view_features'))]
    selected=max(qualifies,key=lambda s:(results[f'{s:.2f}']['views']['predicted_view_lemma_pos'],results[f'{s:.2f}']['views']['predicted_view_features'],-s))
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P4_HEAD_SOURCE_CHANGED');original_freeze()
    seal={'head_strength':selected,'selected_on':'DEV_ONLY','rank_fitting_started':False,'CALIB_started':False,
          'head_model_sha256':digest(DEST/'head-model.json'),'arms':results,'TEST_opened':False}
    atomic_json(LOCAL/'head-selection.json',seal);atomic_json(DEST/'head-selection.json',seal)
    print(json.dumps({'stage':'P4_HEAD_SELECTED','head_strength':selected}),flush=True)


if __name__=='__main__':main()
