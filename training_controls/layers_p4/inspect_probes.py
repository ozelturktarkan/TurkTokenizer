"""Authored counterexamples and exact question margins after sealed selection."""
import json
from s06e_p4 import Tokenizer,Codec
from grammar_p3 import QUESTION_IDS
from training_controls.grammar_p3.validate import PROBES
from .common import DEST,LOCAL,read,require,atomic_json,check_output


def main():
    require(not (LOCAL/'postfit-probes.json').exists(),'P4_REFUSE_OVERWRITE_PROBES')
    comp=read(LOCAL/'comparison.json');require(comp['status']=='EXPERIMENT_COMPLETE','P4_UNSEALED_PROBES')
    names=list(dict.fromkeys(['P2']+(['H'] if 'H' in comp['configs'] else [])+[comp['DEV_selected'],comp['retained']]))
    results={}
    for name in names:
        rt=Tokenizer(**comp['configs'][name]);codec=Codec(**comp['configs'][name]);codec.native=rt
        rows=[];blocks=0;question=None
        for text,word,lemma,pos in PROBES:
            raw=rt._raw_schema_sentence(text);out=rt.analyze_prepared(raw);blocks+=check_output(rt,raw,out)
            require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==text,'P4_PROBE_ROUNDTRIP')
            i,t=next((i,t) for i,t in enumerate(out['tokens']) if t['raw']==word);v=t['lexical_decision']['preferred_view']
            rows.append({'text':text,'word':word,'expected':[lemma,pos],'predicted':[v['lemma'],v['output_pos']] if v else None,
                         'matches':bool(v and [v['lemma'],v['output_pos']]==[lemma,pos])})
            if text=='Sen geldin mi?':
                m=rt.context_selector.s06e_marginals[i]
                q=max(m[a['analysis_id']] for a in t['analysis']['analyses'] if a.get('lexeme_id') in QUESTION_IDS)
                question={'gap_below_winner':max(m.values())-q,'view':v,'question_candidate_present':True}
        results[name]={'probes':rows,'matched':sum(r['matches'] for r in rows),'roundtrips':len(rows),
                       'objective_blocks':blocks,'question_scores':question}
        print(json.dumps({'stage':'P4_PROBES','configuration':name,'matched':results[name]['matched'],'question_gap':question['gap_below_winner']}),flush=True)
    result={'scope':'AUTHORED_DIAGNOSTIC_NOT_INDEPENDENT_TEST','selection_changed':False,'arms':results}
    atomic_json(LOCAL/'postfit-probes.json',result);atomic_json(DEST/'postfit-probes.json',result)


if __name__=='__main__':main()
