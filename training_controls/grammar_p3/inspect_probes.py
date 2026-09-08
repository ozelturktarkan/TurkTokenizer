"""Post-selection diagnostics for the two joint arms; no model tuning."""
import json
from s06e_p3 import Tokenizer,Codec
from .common import DEST,LOCAL,read,atomic_json,require
from .validate import run,PROBES
from .evaluate import clear


def main():
    require(not (LOCAL/'exploratory-probes.json').exists(),'P3_REFUSE_OVERWRITE_PROBES')
    require(read(LOCAL/'comparison.json')['status']=='EXPERIMENT_COMPLETE','P3_UNSEALED_SELECTION')
    result={'scope':'AUTHORED_POST_SELECTION_DIAGNOSTIC_NOT_INDEPENDENT_TEST','selection_changed':False,'arms':{}}
    for name in ('JOINT_HALF','JOINT_FULL'):
        rt=Tokenizer(name);codec=Codec(name);codec.native=rt
        result['arms'][name]=run(rt,codec,PROBES);clear(rt)
        print(json.dumps({'configuration':name,'matched':result['arms'][name]['matched'],'total':len(PROBES)}),flush=True)
    atomic_json(LOCAL/'exploratory-probes.json',result);atomic_json(DEST/'exploratory-probes.json',result)


if __name__=='__main__':main()
