"""Fixed question-signature alignment, with fresh full decoding and audit."""
import copy
import gzip
import json
import time
from bootstrap import ROOT
from s06e_p2_question import Tokenizer,Codec,QuestionNgram
from a123_measurement import measure,summarize
from analysis_schema_s06e import signature
from training_controls.a3_epoch.train import check_output
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import verify_freeze,require
from training_controls.phonology_p1.evaluate import inventory
from .fit import DEST,LOCAL,PARENT
from .evaluate import records,projection_rows,view_summary
from .validate_policy import PROBES


def main():
    # Attempt 1 stopped after two DEV records: its order-invariance probe
    # reversed shared cache lists. Preserve that failed attempt; isolate probes.
    dest=DEST/'question-aligned-r2'; local=LOCAL/'question-aligned-r2'
    require(not dest.exists() and not local.exists(),'P2_Q_REFUSE_OVERWRITE')
    dest.mkdir(); local.mkdir()
    frozen={**read(LOCAL/'policy-imst/evaluation-freeze.json'),**{n:digest(ROOT/n) for n in [
        's06e_p2_question.py','training_controls/lexical_p2/evaluate_question.py','training_controls/lexical_p2/question-protocol.json']}}
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P2_Q_BASE_CHANGED')
    atomic_json(local/'freeze.json',frozen)
    oldfreeze=read(PARENT/'A2/freeze.json'); verify_freeze(PARENT/'A2',oldfreeze)
    rt=Tokenizer(); codec=Codec(); codec.native=rt
    # Compare the adapter directly against the frozen model on mapped tags.
    ng=rt.context_selector.ngram; aux=signature('AUX',{'VerbForm':'Fin'})
    part=signature('PART',{'VerbForm':'Fin'}); noun=signature('NOUN',{})
    assert ng.transition(noun,part,noun)==ng.base.transition(noun,aux,noun)
    assert ng.transition(noun,noun,noun)==ng.base.transition(noun,noun,noun)
    probes=[]
    for text,word,lemma,pos in PROBES:
        raw=rt._raw_schema_sentence(text); snapshot=copy.deepcopy(raw)
        out=rt.analyze_prepared(raw); check_output(rt,raw,out); assert raw==snapshot
        assert codec.decode(codec.encode_from_analysis(out)['input_ids'])==text
        v=next(t for t in out['tokens'] if t['raw']==word)['lexical_decision']['preferred_view']
        probes.append({'text':text,'word':word,'expected':[lemma,pos],'view':v,
                       'matches':bool(v and [v['lemma'],v['output_pos']]==[lemma,pos])})
    raw=copy.deepcopy(rt._raw_schema_sentence(PROBES[4][0])); expected=rt.analyze_prepared(raw)
    for t in raw['tokens']:t['analysis']['analyses'].reverse()
    actual=rt.analyze_prepared(raw)
    assert [t['lexical_decision'] for t in expected['tokens']]==[t['lexical_decision'] for t in actual['tokens']]
    probe_summary={'status':'ADAPTER_AND_API_CONTRACTS_PASS','authored_probes':len(probes),
        'matched':sum(p['matches'] for p in probes),'scope':'AUTHORED_DIAGNOSTIC_NOT_INDEPENDENT_TEST','probes':probes}
    atomic_json(local/'runtime-contracts.json',probe_summary)
    results={}; started=time.monotonic()
    for split in ('dev','calib'):
        folder=dest/split;folder.mkdir()
        refs=list(records(ROOT/f'training/a1-large-v1/{split}.jsonl'))
        prior=records(DEST/'policy-imst/evaluation/1.00'/split/'outputs.jsonl.gz')
        nn=[]; vv=[]; blocks=0
        with gzip.open(folder/'outputs.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as stream:
            for n,(ref,p) in enumerate(zip(refs,prior,strict=True),1):
                require(ref['id']==p['id'],'P2_Q_REFERENCE_ORDER')
                raw=rt._raw_schema_sentence(ref['text'])
                require(inventory(raw)==inventory(p['output']),'P2_Q_NATIVE_CANDIDATES_CHANGED')
                out=rt.analyze_prepared(raw);blocks+=check_output(rt,raw,out)
                nn.extend(measure(ref,out)); vv.extend(projection_rows(ref,out,rt.head.views))
                require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==ref['text'],'P2_Q_ROUNDTRIP')
                stream.write(json.dumps({'id':ref['id'],'output':out},ensure_ascii=False)+'\n')
                if n%50==0 or n==len(refs):print(json.dumps({'stage':'QALIGN','split':split,'sentences':n,'total':len(refs),'seconds':round(time.monotonic()-started,1)}),flush=True)
        for name,rows in [('native-words',nn),('view-words',vv)]:
            with gzip.open(folder/(name+'.jsonl.gz'),'wt',encoding='utf-8') as f:
                for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
        result={'legacy':summarize(nn),'views':view_summary(vv),'objective_blocks_verified':blocks,
            'BPE_roundtrips':len(refs),'artifact_sha256':{p.name:digest(p) for p in folder.iterdir() if p.is_file()}}
        atomic_json(folder/'summary.json',result);results[split]=result
        atomic_json(local/'progress-summary.json',results)
        print(json.dumps({'stage':'QALIGN_SPLIT_COMPLETE','split':split,**result},ensure_ascii=False),flush=True)
    verify_freeze(PARENT/'A2',oldfreeze)
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'P2_Q_EVALUATED_SOURCE_CHANGED')
    old=read(LOCAL/'policy-imst/comparison.json')['arms']['1.00']
    safe=all(results[s]['legacy']['preferred_lemma_pos']>=old[s]['legacy']['preferred_lemma_pos'] and
        results[s]['legacy']['preferred_declared_features']>=old[s]['legacy']['preferred_declared_features'] and
        results[s]['legacy']['legacy_selected_lemma_wrong']<=old[s]['legacy']['legacy_selected_lemma_wrong'] for s in ('dev','calib'))
    final={'status':'EXPERIMENT_COMPLETE','results':results,'nonregression_against_policy':safe,
        'recommended_entry':'s06e_p2_question' if safe else 's06e_p2_policy','new_training':False,
        'new_candidates':False,'TEST_opened':False,'default_promoted':False,
        'seconds':round(time.monotonic()-started,1),'authored_probes_matched':probe_summary['matched']}
    atomic_json(local/'comparison.json',final);atomic_json(dest/'comparison.json',final)
    print(json.dumps({'stage':'QALIGN_COMPLETE','nonregression_against_policy':safe}),flush=True)


if __name__=='__main__':main()
