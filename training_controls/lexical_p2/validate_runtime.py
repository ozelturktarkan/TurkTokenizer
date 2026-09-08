"""P2 public API contracts, independently recomputed objective and ID checks."""
import copy
import json
import tempfile
from pathlib import Path
from bootstrap import ROOT
from s06e_p2 import Tokenizer
from s06e_p2bpe import Tokenizer as Codec
from s06e_r5bpe import Tokenizer as OldCodec
from training_controls.a3_epoch.train import check_output
from training_controls.e70p9.epoch_control import digest,atomic_json


def main():
    rt=Tokenizer(.5); codec=Codec(.5); codec.native=rt; old=OldCodec()
    assert codec.entries==old.entries and codec.lookup==old.lookup and codec.surfaces==old.surfaces
    tests=['Duygusal insanlar güzelliğinden söz etti.', 'İşletmecilerinden biri geldi.',
           'Sen kurnazı gördün mü?', 'Mi notasını çaldım.', "Taylor’ın sözünü İMKB’ye ilettim.",
           '  I\u0307zmir’e\t gittim.\r\n', '', '😀\x00', '```python\nx = "güzellik"\n```']
    blocks=0; roundtrips=0
    for text in tests:
        raw=rt._raw_schema_sentence(text); saved=copy.deepcopy(raw)
        out=rt.analyze_prepared(raw); assert raw==saved
        blocks+=check_output(rt,raw,out)
        assert out['tokens']==rt.analyze_sentence(text)['tokens']
        snap=copy.deepcopy(out)
        for policy in ('selective','available'):
            assert codec.decode(codec.encode_from_analysis(out,policy)['input_ids'])==text; roundtrips+=1
        assert out==snap
        assert codec.decode(codec.encode(text))==text; roundtrips+=1
        for t in out['tokens']:
            p=t['context_decision']['preferred_analysis']; v=t['lexical_decision']['preferred_view']
            assert (p is None)==(v is None)
            if p:
                assert p['analysis_id']==v['analysis_id']
                assert v['root_lemma']==p['lemma']
    pristine=rt.analyze_sentence(tests[0]); changed=copy.deepcopy(pristine)
    for t in changed['tokens']:
        for a in t['lexical_analyses']:
            for v in a['lexical_views']: v['lemma']='CORRUPTED'
    assert rt.analyze_sentence(tests[0])==pristine
    raw=rt._raw_schema_sentence(tests[2]); expected=rt.analyze_prepared(raw)
    for t in raw['tokens']: t['analysis']['analyses'].reverse()
    actual=rt.analyze_prepared(raw)
    assert [t['context_decision']['preferred_analysis'] for t in expected['tokens']]==[t['context_decision']['preferred_analysis'] for t in actual['tokens']]
    assert [t['lexical_decision'] for t in expected['tokens']]==[t['lexical_decision'] for t in actual['tokens']]
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'bad.json'; p.write_text('{}',encoding='utf-8')
        try: Tokenizer(.5,head_path=p)
        except ValueError as exc: assert str(exc)=='P2_HEAD_HASH_MISMATCH'
        else: raise AssertionError('Bad head accepted')
    class Forbidden:
        def analyze_sentence(self,text): raise AssertionError('Code entered morphology')
    codec.native=Forbidden(); assert codec.decode(codec.encode(tests[-1]))==tests[-1]
    b=bytes(range(256)); assert codec.decode_bytes(codec.encode_bytes(b))==b
    assert codec.encode_bytes(b)==old.encode_bytes(b)
    result={'status':'PASS','texts':len(tests),'roundtrips':roundtrips+1,'objective_blocks':blocks,
        'BPE_IDs_preserved':len(codec.entries),'all_256_bytes':True,'cache_and_order_invariance':True,
        'no_output_mutation':True,'wrong_head_rejected':True,'protected_code_bypass':True,
        'sources':{n:digest(ROOT/n) for n in ['analysis_schema_p2.py','s06e_p2.py','s06e_p2bpe.py','training_controls/lexical_p2/validate_runtime.py']}}
    atomic_json(ROOT/'results_lexical_p2/runtime-contracts.json',result); print(json.dumps(result),flush=True)


if __name__=='__main__': main()
