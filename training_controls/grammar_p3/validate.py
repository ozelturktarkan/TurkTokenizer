import copy
import json
import time
from bootstrap import ROOT
from s06e_p2_policy import Tokenizer as P2
from s06e_p3 import Tokenizer,Codec
from grammar_p3 import CHANNELS,VERSION
from .common import check_output,original_freeze,atomic_json,LOCAL,digest

PROBES=[('Sen geldin mi?','mi','mi','AUX'),('Sen geliyor musun?','musun','mi','AUX'),
        ('Mi notasını çaldım.','Mi','mi','NOUN'),('Senin evin büyük.','evin','ev','NOUN'),
        ('Evin kapısı açık.','Evin','ev','NOUN'),('Ali ve ben geldik.','geldik','gel','VERB'),
        ('Ali benimle geldi.','geldi','gel','VERB'),('Senin geldiğini biliyorum.','biliyorum','bil','VERB'),
        ('Okula doğru yürüdü.','doğru','doğru','ADP'),('Doğru cevap bu.','Doğru','doğru','ADJ'),
        ('Onlar geldi.','geldi','gel','VERB'),('Onlar geldiler.','geldiler','gel','VERB'),
        ('Güzel mi güzel bir ev.','mi','mi','AUX'),('Kitabı okudu Ali.','Kitabı','kitap','NOUN'),
        ('Güzelliğinden söz ettim.','Güzelliğinden','güzellik','NOUN')]


def run(rt,codec,texts):
    rows=[];blocks=0
    for text,word,lemma,pos in texts:
        raw=rt._raw_schema_sentence(text);saved=copy.deepcopy(raw)
        out=rt.analyze_prepared(raw);blocks+=check_output(rt,raw,out)
        assert raw==saved
        assert codec.decode(codec.encode_from_analysis(out)['input_ids'])==text
        t=next(t for t in out['tokens'] if t['raw']==word);v=t['lexical_decision']['preferred_view']
        rows.append({'text':text,'word':word,'expected':[lemma,pos],
                     'predicted':[v['lemma'],v['output_pos']] if v else None,
                     'matches':bool(v and [v['lemma'],v['output_pos']]==[lemma,pos]),
                     'native_analysis_id':t['context_decision']['preferred_analysis']['analysis_id']})
    return {'probes':rows,'matched':sum(r['matches'] for r in rows),'objective_blocks':blocks,'roundtrips':len(rows)}


def main():
    before=original_freeze();base=P2(1.)
    model={'version':VERSION,'P2_head_sha256':base.head.sha256,'frame_counts':{'güven|Act':{'Dat':10}},'local_models':{}}
    zero=Tokenizer(model=model);codec=Codec(model=model);codec.native=zero
    for text,*_ in PROBES:
        raw=base._raw_schema_sentence(text);expected=base.analyze_prepared(raw);out=zero.analyze_prepared(raw)
        assert expected['tokens']==out['tokens']
        assert expected['global_solutions']==out['global_solutions']
        check_output(zero,raw,out)
    theta=[0.]*len(CHANNELS)
    for key,value in [('agr.finite_question',1.),('agr.question_carrier_match',.5),('gov.adp_match',.5),('plan.gov.adp_match',.5)]:theta[CHANNELS.index(key)]=value
    rt=Tokenizer(model=model,theta=theta);codec=Codec(model=model,theta=theta);codec.native=rt
    result=run(rt,codec,PROBES)
    raw=copy.deepcopy(rt._raw_schema_sentence('Sen geldin mi?'));expected=rt.analyze_prepared(raw)
    for t in raw['tokens']:t['analysis']['analyses'].reverse()
    actual=rt.analyze_prepared(raw)
    assert [t['lexical_decision'] for t in expected['tokens']]==[t['lexical_decision'] for t in actual['tokens']]
    rt.p3_a2={'lemma_threshold':1.,'feature_threshold':1.}
    direct=rt.analyze_sentence('Sen geldin mi?')
    replay=rt.analyze_prepared(rt._raw_schema_sentence('Sen geldin mi?'))
    assert direct==replay
    bad=copy.deepcopy(model);bad['P2_head_sha256']='bad'
    try:Tokenizer(model=bad)
    except ValueError as exc:assert str(exc)=='P3_P2_BASE_CHANGED'
    else:raise AssertionError('Wrong base model accepted')
    assert original_freeze()==before
    result.update(status='INTEGRATION_CONTRACTS_PASS',model_scope='HAND_SET_INTEGRATION_WEIGHTS_NOT_A_TRAINED_RESULT',
                  zero_contribution_sentences=len(PROBES),candidate_order_invariance=True,
                  calibrated_direct_equals_replay=True,TEST_opened=False)
    LOCAL.mkdir(exist_ok=True)
    atomic_json(LOCAL/'pretraining-contracts.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='probes'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
