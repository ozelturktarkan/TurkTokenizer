"""Integration checks and authored context probes for the IMST policy head."""
import copy
import json
import tempfile
from pathlib import Path
from bootstrap import ROOT
from s06e_p2_policy import Tokenizer,Codec
from training_controls.a3_epoch.train import check_output
from training_controls.e70p9.epoch_control import digest,atomic_json

PROBES=[('Bu duygusal bir konuşmaydı.','duygusal','duygusal','ADJ'),
        ('Bu fiziksel bir engel.','fiziksel','fiziksel','ADJ'),
        ('Güzelliğinden söz ettim.','Güzelliğinden','güzellik','NOUN'),
        ('İşletmecilerinden biri geldi.','İşletmecilerinden','işletmeci','NOUN'),
        ('Sen geldin mi?','mi','mi','AUX'),('Mi notasını çaldım.','Mi','mi','NOUN'),
        ('Evlerimizden biri yandı.','Evlerimizden','ev','NOUN'),
        ('Senin evin güzel.','evin','ev','NOUN')]


def main():
    rt=Tokenizer(1.); codec=Codec(1.); codec.native=rt
    results=[]; blocks=0
    for text,word,lemma,pos in PROBES:
        raw=rt._raw_schema_sentence(text); saved=copy.deepcopy(raw)
        out=rt.analyze_prepared(raw); assert raw==saved
        blocks+=check_output(rt,raw,out)
        assert out['experiment']['export_policy']=='UD_IMST'
        assert out['experiment']['lexical_head_sha256']==rt.head.sha256
        assert out['tokens']==rt.analyze_sentence(text)['tokens']
        encoded=codec.encode_from_analysis(out)
        assert encoded['export_policy']=='UD_IMST' and codec.decode(encoded['input_ids'])==text
        t=next(t for t in out['tokens'] if t['raw']==word)
        v=t['lexical_decision']['preferred_view']
        results.append({'text':text,'word':word,'expected_lemma':lemma,'expected_pos':pos,
            'predicted_view':v,'matches':bool(v and (v['lemma'],v['output_pos'])==(lemma,pos))})
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'bad.json'; p.write_text('{}',encoding='utf-8')
        try: Tokenizer(head_path=p)
        except ValueError as exc: assert str(exc)=='P2_POLICY_HEAD_HASH_MISMATCH'
        else: raise AssertionError('Wrong policy head accepted')
    word=rt.analyze_word('duygusal')
    assert word['analysis_schema']['export_policy']=='UD_IMST'
    try: codec.encode_from_analysis({'tokenizer_version':'S06E-E05-P2-v0.1.0','experiment':{'residual_strength':1.}})
    except ValueError as exc: assert str(exc)=='P2_POLICY_CODEC_REQUIRES_IMST_OUTPUT'
    else: raise AssertionError('Foreign policy output accepted')
    result={'status':'API_CONTRACTS_PASS','objective_blocks':blocks,'roundtrips':len(PROBES),
        'authored_probes':len(PROBES),'authored_probes_matched':sum(r['matches'] for r in results),
        'probe_scope':'AUTHORED_DIAGNOSTIC_NOT_INDEPENDENT_TEST','probes':results,
        'source_sha256':{n:digest(ROOT/n) for n in ['s06e_p2_policy.py','training_controls/lexical_p2/validate_policy.py']}}
    atomic_json(ROOT/'results_lexical_p2/policy-imst/runtime-contracts.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='probes'},ensure_ascii=False),flush=True)


if __name__=='__main__': main()
