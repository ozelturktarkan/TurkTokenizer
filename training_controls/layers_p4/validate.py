import copy
import json
from s06e_p2_policy import Tokenizer as P2
from s06e_p4 import Tokenizer,Codec,AlignedRanker
from features_p4 import Features,VERSION,emitted_positives
from training_controls.grammar_p3.validate import PROBES
from .common import ROOT,LOCAL,read,atomic_json,original_freeze,check_output


def main():
    before=original_freeze();base=P2(1.)
    key='OLD:'+json.dumps(['POS','AUX'],separators=(',',':'))
    model={'version':VERSION,'P2_head_sha256':base.head.sha256,'frames':{},'view_weights':{key:50.},
           'rank_models':{'base_head':{key:50.}},'rank_head_strengths':{'base_head':0.}}
    zero=Tokenizer(model=model);head=Tokenizer(model=model,head_strength=1.)
    rank=Tokenizer(model=model,rank_strength=1.);codec=Codec(model=model);codec.native=zero
    assert not isinstance(rank.context_selector.reference_ua.ranker,AlignedRanker)
    texts=[p[0] for p in PROBES]+['','  I\u0307zmir’e 3,5\tgit.\r\n','Kod: `x = 1`\nqzx_123 😊']
    blocks=0
    for text in texts:
        raw=base._raw_schema_sentence(text);saved=copy.deepcopy(raw);old=base.analyze_prepared(raw);out=zero.analyze_prepared(raw)
        assert old['tokens']==out['tokens'] and old['global_solutions']==out['global_solutions'];blocks+=check_output(zero,raw,out)
        exported=head._finish(copy.deepcopy(old))
        assert old['global_solutions']==exported['global_solutions']
        assert [t['context_decision'] for t in old['tokens']]==[t['context_decision'] for t in exported['tokens']]
        assert [t.get('decision_layers') for t in old['tokens']]==[t.get('decision_layers') for t in exported['tokens']]
        assert codec.decode(codec.encode_from_analysis(exported)['input_ids'])==text
        assert raw==saved
    raw=copy.deepcopy(rank._raw_schema_sentence('Sen geldin mi?'));normal=rank.analyze_prepared(raw);blocks+=check_output(rank,raw,normal)
    assert codec.decode(codec.encode_from_analysis(normal)['input_ids'])==raw['raw']
    i,t=next((i,t) for i,t in enumerate(raw['tokens']) if t['raw']=='mi')
    a=t['analysis']['analyses'][0];v=rank.head.views.options(a)[0];f=Features().rank(raw['tokens'],i,a,v)
    changed=copy.deepcopy(raw['tokens'])
    for token in changed:token.update(gold={'lemma':'invented'},context_decision={'preferred_analysis':{'lemma':'invented'}})
    assert Features().rank(changed,i,a,v)==f
    for token in raw['tokens']:token['analysis']['analyses'].reverse()
    reversed_out=rank.analyze_prepared(raw)
    assert [t['lexical_decision']['native_preferred_analysis_id'] for t in normal['tokens']]==[t['lexical_decision']['native_preferred_analysis_id'] for t in reversed_out['tokens']]
    # A latent correct view is not a positive when the emitted view is wrong.
    class FakeHead:
        def token(self,tokens,i):return {x['analysis_id']:{'view':{'lemma':'wrong','output_pos':'NOUN','features':{}}} for x in tokens[i]['analysis']['analyses']}
    assert not emitted_positives(raw['tokens'],i,{'lemma':'mi','upos':'AUX','feats':{}},False,FakeHead())
    rank.p4_a2={'lemma_threshold':1.,'feature_threshold':1.}
    assert rank.analyze_sentence('Sen geldin mi?')==rank.analyze_prepared(rank._raw_schema_sentence('Sen geldin mi?'))
    try:Tokenizer(model=model,head_strength=.5,rank_strength=1.)
    except ValueError as e:assert str(e)=='P4_RANK_HEAD_ALIGNMENT_MISMATCH'
    else:raise AssertionError('Mismatched emitted-head ranker accepted')
    assert original_freeze()==before
    summary={'status':'PRETRAINING_CONTRACTS_PASS','zero_control_sentences':len(texts),'head_only_native_invariance':True,
             'ranked_objective_blocks':blocks,'BPE_roundtrips':len(texts)+1,'no_gold_or_selected_neighbour_features':True,
             'emitted_positive_label_contract':True,'single_A2_pass':True,'candidate_order_invariance':True,
             'scope':'HAND_SET_WEIGHTS_ENGINEERING_TEST_NOT_TRAINED_ACCURACY','TEST_opened':False}
    LOCAL.mkdir(exist_ok=True);atomic_json(LOCAL/'pretraining-contracts.json',summary);print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
