"""Explain residual feature limits; this audit never changes fitted weights."""
import json
from grammar_p3 import CHANNELS,active
from .common import DEST,LOCAL,read,records,digest,atomic_json,require


def main():
    require(not (LOCAL/'feature-diagnostics.json').exists(),'P3_REFUSE_OVERWRITE_DIAGNOSTICS')
    model=read(DEST/'model.json');meta=read(LOCAL/'model-location.json')
    require(digest(DEST/'model.json')==meta['sha256'],'P3_DIAGNOSTIC_MODEL_CHANGED')
    result={'scope':'TRAIN_ROUND_1_RETAINED_CONTRASTS_BEFORE_LAST_FIT_NOT_TEST_ACCURACY','arms':{},
            'model_sha256':meta['sha256'],'weights_changed':False}
    for arm,name in [('government','GOV'),('agreement','AGR'),('combined','JOINT_FULL')]:
        rows=list(records(DEST/f'ranking/{arm}-round-1.jsonl.gz'))
        wrong=[r for r in rows if r['gap']<0]
        def flat(r):return not any(abs(v)>1e-12 for k,v in zip(CHANNELS,r['x']) if active(k,arm))
        result['arms'][name]={'contrasts':len(rows),'wrong_at_round_1_mining':len(wrong),
                             'indistinguishable_by_active_features':sum(flat(r) for r in rows),
                             'wrong_and_indistinguishable':sum(flat(r) for r in wrong),
                             'nonzero_learned_weights':{k:v for k,v in zip(CHANNELS,model['configurations'][name]['theta']) if abs(v)>1e-12}}
    atomic_json(LOCAL/'feature-diagnostics.json',result);atomic_json(DEST/'feature-diagnostics.json',result)
    print(json.dumps({k:{n:v for n,v in r.items() if n!='nonzero_learned_weights'} for k,r in result['arms'].items()}),flush=True)


if __name__=='__main__':main()
