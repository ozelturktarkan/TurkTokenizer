"""Calibrate native abstention after DEV selection, without changing ranking."""
import copy
import json
from pathlib import Path
from s06e_p4 import Tokenizer,Codec
from a123_measurement import a2_summary
from training_controls.a2_calibration.calibrate import choose,validate_application
from .common import ROOT,DEST,LOCAL,HERE,read,records,digest,atomic_json,require,original_freeze


def main():
    require(not (DEST/'A2').exists(),'P4_REFUSE_OVERWRITE_A2')
    (DEST/'A2').mkdir();comparison=read(LOCAL/'comparison.json');cfg=read(HERE/'protocol.json')['A2']
    require(comparison['status']=='EXPERIMENT_COMPLETE','P4_EVALUATION_INCOMPLETE')
    name=comparison['retained'];results={}
    for key in dict.fromkeys(['P2',name]):
        result=comparison['arms'][key]['calib'];folder=Path(result['output_path']).parent
        require(all(digest(folder/n)==h for n,h in result['artifact_sha256'].items()),'P4_CALIB_ARTIFACT_CHANGED')
        rows=list(records(folder/'native-words.jsonl.gz'))
        grid,best=choose(rows,cfg['grid'],cfg['target'])
        atomic_json(DEST/'A2'/f'{key}-grid.json',grid)
        thresholds=best['thresholds'] if best else None
        zero={'lemma_threshold':0.,'feature_threshold':0.}
        checks=[zero]+([thresholds] if thresholds and thresholds!=zero else [])
        counts=[0]*len(checks);roundtrips=0
        args=comparison['configs'][key];rt=Tokenizer(**args,a2=thresholds);codec=Codec(**args,a2=thresholds);codec.native=rt
        refs=list(records(ROOT/'training/a1-large-v1/calib.jsonl'))
        for ref,rec in zip(refs,records(folder/'outputs.jsonl.gz'),strict=True):
            require(ref['id']==rec['id'],'P4_CALIB_ALIGNMENT')
            for i,t in enumerate(checks):
                _,accepted=validate_application(ref,rec['output'],t);counts[i]+=accepted
            if thresholds:
                expected,_=validate_application(ref,rec['output'],thresholds)
                actual=rt._finish(copy.deepcopy(rec['output']))
                require([t.get('context_decision') for t in actual['tokens']]==[t.get('context_decision') for t in expected['tokens']],'P4_LIVE_CALIBRATION_MISMATCH')
                require([t.get('decision_layers') for t in actual['tokens']]==[t.get('decision_layers') for t in expected['tokens']],'P4_LIVE_LAYER_MISMATCH')
                require(codec.decode(codec.encode_from_analysis(actual)['input_ids'])==ref['text'],'P4_A2_BPE_ROUNDTRIP')
                roundtrips+=1
        require(counts==[a2_summary(rows,t)['accepted'] for t in checks],'P4_CALIB_ACCEPTANCE_COUNT')
        dev=comparison['arms'][key]['dev'];devrows=list(records(Path(dev['output_path']).parent/'native-words.jsonl.gz'))
        results[key]={'selected':best,'status':'CALIBRATED_EXPERIMENTAL' if best else 'TARGET_INFEASIBLE_ON_PREDECLARED_GRID',
                      'zero_threshold':a2_summary(rows,zero),'grid_pairs':len(grid),
                      'feasible_pairs':sum(bool(r['accepted'] and r['lemma_precision_pct']>=92 and r['feature_precision_pct']>=92) for r in grid),
                      'DEV_at_CALIB_thresholds':a2_summary(devrows,thresholds) if thresholds else None,
                      'checks':{'online_offline_configs':checks,'accepted':counts,'runtime_calibrated_BPE_roundtrips':roundtrips},
                      'native_output_sha256':digest(folder/'outputs.jsonl.gz')}
        print(json.dumps({'stage':'P4_A2_COMPLETE','configuration':key,'status':results[key]['status'],'selected':best}),flush=True)
    winner=results[name]
    selection={'status':winner['status'],'name':name,'configuration':comparison['configs'][name],'A2_config':winner['selected']['thresholds'] if winner['selected'] else None,
               'model_sha256':comparison['model_sha256'],'DEV_selection_sha256':digest(LOCAL/'dev-selection-seal.json'),
               'comparison_sha256':digest(LOCAL/'comparison.json'),'calibration_scope':'NATIVE_LEMMA_POS_AND_DECLARED_FEATURES',
               'lexical_view_confidence_calibrated':False,'full_morpheme_path_accuracy_measured':False,
               'TEST_opened':False,'default_promoted':False}
    result={'status':'A2_VERIFIED','arms':results,'selection':selection,'source_sha256':digest(HERE/'calibrate.py')}
    original_freeze()
    atomic_json(LOCAL/'calibration.json',result);atomic_json(DEST/'A2/summary.json',result)
    atomic_json(LOCAL/'selection.json',selection);atomic_json(DEST/'selection.json',selection)


if __name__=='__main__':main()
