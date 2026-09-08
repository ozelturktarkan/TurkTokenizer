"""Exact retained-search margins for the unresolved authored question probe."""
import json
from s06e_p3 import Tokenizer
from grammar_p3 import QUESTION_IDS
from .common import DEST,LOCAL,read,require,atomic_json,check_output
from .evaluate import clear


def main():
    require(not (LOCAL/'question-score-audit.json').exists(),'P3_REFUSE_OVERWRITE_QUESTION_AUDIT')
    require(read(LOCAL/'comparison.json')['status']=='EXPERIMENT_COMPLETE','P3_UNSEALED_AUDIT')
    result={'text':'Sen geldin mi?','scope':'AUTHORED_DIAGNOSTIC_RETAINED_SEARCH_MAX_MARGINALS','arms':{},'weights_changed':False}
    for name in ('C0_P2','JOINT_HALF','JOINT_FULL'):
        rt=Tokenizer(name);raw=rt._raw_schema_sentence(result['text']);out=rt.analyze_prepared(raw);check_output(rt,raw,out)
        i,t=next((i,t) for i,t in enumerate(out['tokens']) if t['raw']=='mi');m=rt.context_selector.s06e_marginals[i]
        rows=[]
        for a in t['analysis']['analyses']:
            rows.append({'analysis_id':a['analysis_id'],'native_pos':a['output_pos'],'question_lexeme':a.get('lexeme_id') in QUESTION_IDS,
                         'view_pos':rt.head.token(out['tokens'],i)[a['analysis_id']]['view']['output_pos'],
                         'max_marginal':m[a['analysis_id']]})
        rows.sort(key=lambda r:(-r['max_marginal'],r['analysis_id']))
        question=max(r['max_marginal'] for r in rows if r['question_lexeme'])
        result['arms'][name]={'candidates':rows,'best_question_gap_below_winner':rows[0]['max_marginal']-question,
                              'selected_view':t['lexical_decision']['preferred_view']}
        clear(rt)
    atomic_json(LOCAL/'question-score-audit.json',result);atomic_json(DEST/'question-score-audit.json',result)
    print(json.dumps({k:r['best_question_gap_below_winner'] for k,r in result['arms'].items()}),flush=True)


if __name__=='__main__':main()
