"""Exploratory source-policy ablation, with its own DEV seal and CALIB check."""
import copy
import gzip
import json
import time
from bootstrap import ROOT
from s06e_p2_policy import Tokenizer,Codec
from a123_measurement import measure,summarize
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import verify_freeze,require
from training_controls.a3_epoch.train import check_output
from training_controls.phonology_p1.evaluate import inventory
from .evaluate import records,projection_rows,view_summary
from .fit import DEST,LOCAL,PARENT


def main():
    dest=DEST/'policy-imst/evaluation'; local=LOCAL/'policy-imst'
    require(not dest.exists(),'P2_POLICY_EVAL_REFUSE_OVERWRITE'); dest.mkdir()
    names=['s06e_p2_policy.py','training_controls/lexical_p2/evaluate_policy.py']
    frozen={**read(LOCAL/'evaluation-freeze.json'),**{n:digest(ROOT/n) for n in names}}
    # Newly added files are tracked here; historical mixed-evaluation sources
    # remain exactly those frozen by that experiment.
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P2_POLICY_BASE_CHANGED')
    atomic_json(local/'evaluation-freeze.json',frozen)
    model=read(local/'model-location.json'); oldfreeze=read(PARENT/'A2/freeze.json')
    verify_freeze(PARENT/'A2',oldfreeze)
    started=time.monotonic(); results={}
    def run(strength,split):
        key=f'{strength:.2f}'; folder=dest/key/split; folder.mkdir(parents=True)
        print(json.dumps({'stage':'POLICY_LOAD','strength':strength,'split':split}),flush=True)
        rt=Tokenizer(strength); codec=Codec(strength); codec.native=rt
        refs=list(records(ROOT/f'training/a1-large-v1/{split}.jsonl'))
        native=[]; projected=[]; blocks=0
        baseline=records(PARENT/'P1-phonology-v1/combined'/split/'outputs.jsonl.gz')
        with gzip.open(folder/'outputs.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as out_file:
            for n,(ref,prior) in enumerate(zip(refs,baseline,strict=True),1):
                require(ref['id']==prior['id'],'P2_POLICY_REFERENCE_ORDER')
                if strength==0:
                    # No score change: classify views of the immutable P1
                    # decisions. This control intentionally avoids a re-decode.
                    out=rt._finish(copy.deepcopy(prior['output']))
                    require(measure(ref,out)==measure(ref,prior['output']),'P2_POLICY_CONTROL_CHANGED')
                    require(inventory(out)==inventory(prior['output']),'P2_POLICY_CONTROL_INVENTORY')
                else:
                    raw=rt._raw_schema_sentence(ref['text'])
                    require(inventory(raw)==inventory(prior['output']),'P2_POLICY_INVENTORY_DRIFT')
                    out=rt.analyze_prepared(raw); blocks+=check_output(rt,raw,out)
                native.extend(measure(ref,out)); projected.extend(projection_rows(ref,out,rt.head.views))
                require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==ref['text'],'P2_POLICY_ROUNDTRIP')
                out_file.write(json.dumps({'id':ref['id'],'output':out},ensure_ascii=False)+'\n')
                if n%50==0 or n==len(refs): print(json.dumps({'stage':'POLICY_EVAL','strength':strength,'split':split,'sentences':n,'total':len(refs),'seconds':round(time.monotonic()-started,1)}),flush=True)
        for name,rows in [('native-words',native),('view-words',projected)]:
            with gzip.open(folder/(name+'.jsonl.gz'),'wt',encoding='utf-8') as f:
                for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
        result={'strength':strength,'legacy':summarize(native),'views':view_summary(projected),
            'objective_blocks_verified':blocks,'control_reused_verified_P1_decisions':strength==0,
            'BPE_roundtrips':len(refs),'artifact_sha256':{p.name:digest(p) for p in folder.iterdir() if p.is_file()}}
        require(result['legacy']['words']==(4070 if split=='dev' else 2266),'P2_POLICY_DENOMINATOR')
        atomic_json(folder/'summary.json',result); results.setdefault(key,{})[split]=result
        atomic_json(local/'progress-summary.json',results)
        print(json.dumps({'stage':'POLICY_SPLIT_COMPLETE','split':split,**result},ensure_ascii=False),flush=True)
    run(0.,'dev'); run(1.,'dev')
    base=results['0.00']['dev']['legacy']; candidate=results['1.00']['dev']['legacy']
    selected=1. if all(candidate[k]>=base[k] for k in ['preferred_lemma_pos','preferred_declared_features']) else 0.
    seal={'strength':selected,'selected_on':'DEV_ONLY','head_sha256':model['sha256'],
        'export_policy':'UD_IMST','CALIB_started':False,'source_sha256':frozen}
    atomic_json(local/'dev-selection-seal.json',seal)
    run(0.,'calib')
    if selected: run(1.,'calib')
    verify_freeze(PARENT/'A2',oldfreeze)
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P2_POLICY_EVALUATED_SOURCE_CHANGED')
    historical=read(ROOT/'results_phonology_p1/comparison.json')['arms']['baseline']
    chosen=results[f'{selected:.2f}']
    safe=all(chosen[s]['legacy']['preferred_lemma_pos']>=historical[s]['counts']['preferred_lemma_pos'] and
        chosen[s]['legacy']['preferred_declared_features']>=historical[s]['counts']['preferred_declared_features'] and
        chosen[s]['legacy']['legacy_selected_lemma_wrong']<=historical[s]['counts']['legacy_selected_lemma_wrong'] for s in ('dev','calib'))
    final={'status':'EXPERIMENT_COMPLETE','arms':results,'selected_strength':selected,
        'historical_E05_nonregression':safe,'default_promoted':False,'export_policy':'UD_IMST',
        'exploratory_extension':True,'new_morphological_paths':False,'TEST_opened':False,'BPE_IDs_preserved':224309,
        'seconds':round(time.monotonic()-started,1)}
    atomic_json(local/'comparison.json',final); atomic_json(DEST/'policy-imst/comparison.json',final)
    print(json.dumps({'stage':'POLICY_COMPLETE','selected_strength':selected,'historical_E05_nonregression':safe}),flush=True)


if __name__=='__main__': main()
