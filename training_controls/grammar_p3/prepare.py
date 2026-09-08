import collections
import gzip
import json
import time
from bootstrap import ROOT
from s06e_p2_policy import Tokenizer as P2
from grammar_p3 import Grammar,VERSION
from analysis_schema_p2 import view_matches
from context_ranker import canonical
from .common import DEST,LOCAL,HERE,read,digest,atomic_json,require,records,emit,original_freeze


def main():
    require(not DEST.exists(),'P3_REFUSE_OVERWRITE_PREPARE')
    LOCAL.mkdir(exist_ok=True);DEST.mkdir()
    config=read(HERE/'protocol.json');manifest=read(ROOT/'training/a1-large-v1/manifest.json')
    train=ROOT/'training/a1-large-v1/train.jsonl'
    require(digest(train)==manifest['files']['train.jsonl'],'P3_TRAIN_HASH_CHANGED')
    refs=[r for r in records(train) if r['source_corpus']=='IMST']
    require(len(refs)==3260 and len({r['id'] for r in refs})==3260,'P3_IMST_TRAIN_COUNT')
    frames=collections.defaultdict(collections.Counter)
    for r in refs:
        source={t['source_id']:t for t in r['tokens']}
        for t in r['tokens']:
            h=source.get(t['head'])
            if h and h['upos']=='VERB' and t['upos'] in {'NOUN','PROPN','PRON'} and t['deprel'].split(':')[0] in {'obj','iobj','obl'}:
                from common import lower
                frames[lower(h['lemma'])+'|'+h['feats'].get('Voice','Act')][t['feats'].get('Case','Nom')]+=1
    rt=P2(1.);grammar=Grammar(dict(frames))
    model={'version':VERSION,'P2_head_sha256':rt.head.sha256,'frame_counts':dict(frames),'local_models':{},
           'training_source':'IMST_TRAIN_ONLY','TRAIN_sha256':digest(train),'TRAIN_sentences':len(refs),
           'frame_semantics':'OBSERVED_DEPENDENT_CASES_NOT_EXHAUSTIVE_VALENCY'}
    atomic_json(DEST/'base-model.json',model)
    paths=['grammar_p3.py','s06e_p3.py','decoder_p3.py','training_controls/grammar_p3/prepare.py',
           'training_controls/grammar_p3/common.py','training_controls/grammar_p3/protocol.json','training_controls/grammar_p3/test_grammar.py']
    frozen={**original_freeze(),'source_sha256':{p:digest(ROOT/p) for p in paths},'TRAIN_sha256':digest(train),
            'P2_head_sha256':rt.head.sha256,'TEST_opened':False}
    atomic_json(LOCAL/'prepare-freeze.json',frozen);atomic_json(DEST/'prepare-freeze.json',frozen)
    counts=collections.Counter();freq=collections.Counter();started=time.monotonic()
    with gzip.open(DEST/'train-raw.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as rawout, \
         gzip.open(DEST/'local-features.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as featureout:
        for n,ref in enumerate(refs,1):
            raw=rt._raw_schema_sentence(ref['text']);ts=raw['tokens'];units={(u['start'],u['end']):u for u in ref['units']}
            golds=[];eligible=[]
            for i,t in enumerate(ts):
                u=units.get((t['start'],t['end']));gold=u['gold'] if u else None
                good=[];aa=t['analysis']['analyses'];fs=[];offsets=[];ids=[]
                require(t['analysis']['search_complete'],'P3_TRAIN_SEARCH_INCOMPLETE')
                counts['words_with_analyses']+=bool(aa);counts['analyses']+=len(aa)
                cop=bool(u and u['projection']=='EXPLICIT_SOURCE_NOMINAL_COPULA')
                positive=[a['analysis_id'] for a in aa if any(view_matches(v,gold,True,cop,a) for v in rt.head.views.options(a))]
                golds.append({'gold':gold,'projection':u['projection'] if u else None,'positive_analysis_ids':positive})
                if not gold or not aa or (u and u['punctuation']):continue
                counts['labelled_words']+=1
                if not positive:counts['no_strict_positive']+=1;continue
                counts['strict_positive_available']+=1
                base=rt.context_selector.ranker.token(ts,i)
                for a in {canonical(a):a for a in aa}.values():
                    ids.append(a['analysis_id']);good.append(a['analysis_id'] in positive)
                    fs.append(grammar.local(ts,i,a));offsets.append(base[a['analysis_id']])
                if all(good):counts['noncompetitive']+=1;continue
                if not any(fs):counts['no_local_grammar_evidence']+=1;continue
                row={'context_id':ref['id'],'token':i,'features':fs,'good':good,'offsets':offsets,'analysis_ids':ids}
                emit(featureout,row);counts['local_examples']+=1;counts['candidate_rows']+=len(good)
                freq.update(set().union(*(set(x) for x in fs)));eligible.append(i)
            emit(rawout,{'id':ref['id'],'raw_output':raw,'golds':golds,'eligible_targets':eligible})
            if n%100==0 or n==len(refs):
                print(json.dumps({'stage':'P3_PREPARE','sentences':n,'total':len(refs),'seconds':round(time.monotonic()-started,1),'local_examples':counts['local_examples']}),flush=True)
            if n%200==0:rt.head.views.cache.clear();grammar.transition.cache_clear()
    require(all(digest(ROOT/p)==h for p,h in frozen['source_sha256'].items()),'P3_PREPARE_SOURCE_CHANGED')
    original_freeze()
    atomic_json(DEST/'feature-frequencies.json',dict(freq))
    summary={'status':'PREPARED','TRAIN_sentences':len(refs),'counts':dict(counts),'observed_verb_voice_keys':len(frames),
             'observed_verb_lemmas':len({k.split('|')[0] for k in frames}),
             'artifacts':{p.name:digest(p) for p in DEST.iterdir() if p.is_file()},'seconds':round(time.monotonic()-started,1),
             'candidate_source':'FRESH_FROZEN_P1_COMBINED','TEST_opened':False}
    atomic_json(DEST/'prepare-summary.json',summary);atomic_json(LOCAL/'prepare-summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
