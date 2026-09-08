"""P1 morphology + frozen E05 + independently fitted lexical-view residual."""
import copy
import hashlib
import json
from pathlib import Path

from bootstrap import ROOT
from s06e_p1 import Tokenizer as P1Tokenizer, VERSION as P1_VERSION, E05_SHA256
from s05_ua_features import UARanker
from analysis_schema_p2 import LexicalViews, view_features, VERSION as SCHEMA_VERSION
from r5.engine import fingerprint

VERSION='S06E-E05-P2-v0.1.0'
MODEL_MANIFEST=ROOT/'results_lexical_p2/model-location.json'


class ViewHead:
    def __init__(self, analyzer, head_path=None):
        meta=json.loads(MODEL_MANIFEST.read_text(encoding='utf-8'))
        path=Path(head_path or meta['path']); raw=path.read_bytes()
        self.sha256=hashlib.sha256(raw).hexdigest()
        if self.sha256!=meta['sha256']: raise ValueError('P2_HEAD_HASH_MISMATCH')
        self.model=json.loads(raw)
        if self.model['schema']!=SCHEMA_VERSION or self.model['E05_sha256']!=E05_SHA256:
            raise ValueError('P2_HEAD_SCHEMA_OR_BASE_MISMATCH')
        self.weights=self.model['weights']; self.views=LexicalViews(analyzer)
        self.tokens=None; self.cache={}

    def token(self,tokens,i):
        if self.tokens is not tokens: self.tokens=tokens; self.cache={}
        if i not in self.cache:
            result={}
            for a in tokens[i]['analysis']['analyses']:
                scored=[(sum(self.weights.get(k,0.)*x for k,x in view_features(tokens,i,a,v).items()),v)
                        for v in self.views.options(a)]
                scored.sort(key=lambda item:(-item[0],item[1]['view_id']))
                score,v=scored[0]
                result[a['analysis_id']]={'score':score,'view':v,
                    'view_margin':score-scored[1][0] if len(scored)>1 else None,
                    'views':len(scored)}
            self.cache[i]=result
        return self.cache[i]


class P2Ranker(UARanker):
    def __init__(self,base,head,strength):
        self.base=base; self.head=head; self.strength=strength
        self.model=base.model; self.weights=base.weights; self.segmenter=base.segmenter

    def token(self,tokens,i):
        base=self.base.token(tokens,i)
        if not self.strength: return base
        extra=self.head.token(tokens,i)
        scores={aid:s+self.strength*extra[aid]['score'] for aid,s in base.items()}
        peak=max(scores.values(),default=0.)
        return {aid:s-peak for aid,s in scores.items()}


class Tokenizer(P1Tokenizer):
    def __init__(self,strength=0.,head_path=None,ranker_path=None):
        if strength not in (0.,.25,.5,1.): raise ValueError('P2_UNREGISTERED_STRENGTH')
        super().__init__('combined',ranker_path)
        self.p2_strength=strength; self.head=ViewHead(self.analyzer,head_path)
        def install(selector):
            if isinstance(getattr(selector,'ranker',None),UARanker):
                selector.ranker=P2Ranker(selector.ranker,self.head,strength)
                selector.context_fingerprint=fingerprint([selector.context_fingerprint,self.head.sha256,strength])
            for attr in ('reference_selector','reference_ua'):
                child=getattr(selector,attr,None)
                if child is not None: install(child)
        install(self.context_selector)
        self.context_selector.a123_models['p2_head.json']=self.head.sha256

    def _raw_schema_sentence(self,text):
        out=super()._raw_schema_sentence(text); out['tokenizer_version']=VERSION
        out['p2_inventory']='P1_COMBINED_UNCHANGED'
        return out

    def _finish(self,out):
        out=super()._finish(out); out['tokenizer_version']=VERSION
        out['experiment'].update(id=VERSION,lexical_schema=SCHEMA_VERSION,
            lexical_head_sha256=self.head.sha256,residual_strength=self.p2_strength,
            E05_weights_frozen=True,new_training=True,scoring_weights_frozen=self.p2_strength==0,
            new_training_scope='TRAIN_ONLY_LEXICAL_VIEW_HEAD',new_morphological_paths=False)
        out['analysis_schema']['lexical_view_schema']=SCHEMA_VERSION
        for i,t in enumerate(out['tokens']):
            aa=t['analysis']['analyses']; d=t.get('context_decision',{}); p=d.get('preferred_analysis')
            t['lexical_analyses']=[copy.deepcopy(self.head.views.schema(a)) for a in aa]
            scores=self.head.token(out['tokens'],i)
            best=scores[p['analysis_id']] if p else None
            t['lexical_decision']={'preferred_view':copy.deepcopy(best['view']) if best else None,
                'native_preferred_analysis_id':p['analysis_id'] if p else None,
                'view_margin':best['view_margin'] if best else None,
                'native_model_separated':d.get('selected_analysis') is not None,
                'calibrated_confidence':False,'score':best['score'] if best else None,
                'native_analysis_rewritten':False}
        return out

    def analyze_prepared(self,raw):
        if raw.get('tokenizer_version')!=VERSION or raw.get('p2_inventory')!='P1_COMBINED_UNCHANGED':
            raise ValueError('P2_REPLAY_REQUIRES_P2_INVENTORY')
        if raw.get('manifest',{}).get('grammar_sha256')!=self.analyzer.manifest()['grammar_sha256']:
            raise ValueError('P2_REPLAY_GRAMMAR_MISMATCH')
        return self._finish(self.context_selector.apply(copy.deepcopy(raw)))

    def analyze_word(self,word,n_best=None):
        out=super().analyze_word(word,n_best); out['tokenizer_version']=VERSION
        # Word-only calls expose alternatives; a contextual view is not invented.
        if 'analyses' in out:
            out['lexical_analyses']=[copy.deepcopy(self.head.views.schema(a)) for a in out['analyses']]
        return out
