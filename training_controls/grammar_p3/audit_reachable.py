"""Separate inventory coverage from the fixed lexical head's reachable outputs."""
import collections
import json
from pathlib import Path
from s06e_p2_policy import Tokenizer
from analysis_schema_p2 import view_matches
from .common import ROOT,DEST,LOCAL,read,records,digest,atomic_json,require


def main():
    require(not (LOCAL/'reachable-output-audit.json').exists(),'P3_REFUSE_OVERWRITE_REACHABILITY')
    comp=read(LOCAL/'comparison.json');name=comp['retained_configuration'];rt=Tokenizer(1.);splits={}
    for split in ('dev','calib'):
        info=comp['arms'][name][split];path=Path(info['output_path'])
        require(digest(path)==info['artifact_sha256']['outputs.jsonl.gz'],'P3_REACHABILITY_OUTPUT_CHANGED')
        counts=collections.Counter()
        for ref,rec in zip(records(ROOT/f'training/a1-large-v1/{split}.jsonl'),records(path),strict=True):
            require(ref['id']==rec['id'],'P3_REACHABILITY_REFERENCE_MISMATCH')
            out=rec['output'];spans={(t['start'],t['end']):(i,t) for i,t in enumerate(out['tokens'])}
            for u in ref['units']:
                if u['punctuation']:continue
                counts['words']+=1;pair=spans.get((u['start'],u['end']));gold=u['gold']
                if pair is None:counts['no_matching_view_or_unresolved']+=1;continue
                i,t=pair;aa=t['analysis']['analyses'];scores=rt.head.token(out['tokens'],i)
                p=t.get('context_decision',{}).get('preferred_analysis');chosen=t['lexical_decision']['preferred_view']
                if p:require(scores[p['analysis_id']]['view']==chosen,'P3_HEAD_SELECTION_CHANGED')
                exists=any(view_matches(v,gold) for a in aa for v in rt.head.views.options(a))
                reachable=any(view_matches(item['view'],gold) for item in scores.values())
                correct=bool(chosen and view_matches(chosen,gold))
                counts['inventory_view_oracle']+=exists;counts['fixed_head_reachable_oracle']+=reachable
                if correct:counts['correct_selected_view']+=1
                elif reachable:counts['wrong_but_reachable_by_native_reranking']+=1
                elif exists:counts['view_exists_but_fixed_head_blocks_every_native_choice']+=1
                else:counts['no_matching_view_or_unresolved']+=1
                if not correct and p and any(view_matches(v,gold) for v in rt.head.views.options(p)):
                    counts['wrong_with_correct_view_on_same_selected_native']+=1
            rt.head.views.cache.clear()
        require(counts['correct_selected_view']==info['views']['predicted_view_lemma_pos'],'P3_REACHABILITY_COUNT_MISMATCH')
        require(counts['inventory_view_oracle']==info['views']['oracle_view_lemma_pos'],'P3_REACHABILITY_ORACLE_MISMATCH')
        require(sum(counts[k] for k in ('correct_selected_view','wrong_but_reachable_by_native_reranking','view_exists_but_fixed_head_blocks_every_native_choice','no_matching_view_or_unresolved'))==counts['words'],'P3_REACHABILITY_PARTITION')
        splits[split]=dict(counts)
    total=dict(sum((collections.Counter(r) for r in splits.values()),collections.Counter()))
    result={'configuration':name,'scope':'FROZEN_IMST_HEAD_AND_FIXED_CANDIDATES_NOT_PHYSICAL_GRAMMAR_CAPACITY',
            'splits':splits,'combined':total,'weights_changed':False,'TEST_opened':False}
    atomic_json(LOCAL/'reachable-output-audit.json',result);atomic_json(DEST/'reachable-output-audit.json',result)
    print(json.dumps(total),flush=True)


if __name__=='__main__':main()
