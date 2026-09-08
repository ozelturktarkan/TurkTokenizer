"""P4: independent emitted-view head and output-aligned final rank residual."""
import copy
import hashlib
import json
import math
from pathlib import Path
from bootstrap import ROOT
from s06e_p2_policy import Tokenizer as P2,Codec as P2Codec
from s06e_p2 import VERSION as P2_VERSION
from s05_ua_features import UARanker
from analysis_schema_p2 import view_features
from features_p4 import Features,VERSION as FEATURE_VERSION
from r5.engine import fingerprint
from s06e_a123 import apply_a2

VERSION='S06E-P4-TwoLayers-v0.1.0'
META=ROOT/'results_layers_p4/model-location.json'


class ExportHead:
    def __init__(self,base,features,weights,strength):
        self.base=base;self.features=features;self.weights=weights;self.strength=strength;self.tokens=None;self.cache={}
    def token(self,tokens,i):
        if not self.strength:return self.base.token(tokens,i)
        if self.tokens is not tokens:self.tokens=tokens;self.cache={}
        if i not in self.cache:
            result={}
            for a in tokens[i]['analysis']['analyses']:
                scores=[]
                for v in self.base.views.options(a):
                    frozen=sum(self.base.weights.get(k,0.)*x for k,x in view_features(tokens,i,a,v).items())
                    residual=sum(self.weights.get(k,0.)*x for k,x in self.features.view(tokens,i,a,v).items())
                    scores.append((frozen+self.strength*residual,v))
                scores.sort(key=lambda x:(-x[0],x[1]['view_id']));score,v=scores[0]
                result[a['analysis_id']]={'score':score,'view':v,'views':len(scores),
                    'view_margin':score-scores[1][0] if len(scores)>1 else None}
            self.cache[i]=result
        return self.cache[i]


class AlignedRanker(UARanker):
    def __init__(self,base,features,head,weights,strength):
        self.base=base;self.features=features;self.export_head=head;self.residual_weights=weights;self.strength=strength
        self.model=base.model;self.weights=base.weights;self.segmenter=base.segmenter
    def residual(self,tokens,i,a):
        v=self.export_head.token(tokens,i)[a['analysis_id']]['view']
        return sum(self.residual_weights.get(k,0.)*x for k,x in self.features.rank(tokens,i,a,v).items())
    def token(self,tokens,i):
        base=self.base.token(tokens,i)
        if not self.strength:return base
        scores={a['analysis_id']:base[a['analysis_id']]+self.strength*self.residual(tokens,i,a) for a in tokens[i]['analysis']['analyses']}
        peak=max(scores.values(),default=0.)
        return {k:v-peak for k,v in scores.items()}


class Tokenizer(P2):
    def __init__(self,head_strength=0.,rank_strength=0.,rank_variant='base_head',model=None,model_path=None,a2=None):
        super().__init__(1.)
        if model is None:
            meta=json.loads(META.read_text(encoding='utf-8'));path=Path(model_path or meta['path']);raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('P4_MODEL_HASH_MISMATCH')
            model=json.loads(raw)
        if model['version']!=FEATURE_VERSION or model['P2_head_sha256']!=self.head.sha256:raise ValueError('P4_BASE_OR_SCHEMA_MISMATCH')
        if head_strength not in (0.,.25,.5,1.) or rank_strength not in (0.,.25,.5,1.):raise ValueError('P4_UNREGISTERED_STRENGTH')
        if rank_variant not in {'base_head','selected_head'}:raise ValueError('P4_UNKNOWN_RANK_VARIANT')
        if rank_strength and rank_variant not in model.get('rank_models',{}):raise ValueError('P4_MISSING_RANK_MODEL')
        if rank_strength:
            expected=model['rank_head_strengths'][rank_variant]
            if head_strength!=expected:raise ValueError('P4_RANK_HEAD_ALIGNMENT_MISMATCH')
        self.p4_model=model;self.p4_hash=fingerprint(model);self.head_strength=head_strength;self.rank_strength=rank_strength
        self.rank_variant=rank_variant;self.p4_a2=a2;self.features=Features(model.get('frames',{}))
        self.export_head=ExportHead(self.head,self.features,model.get('view_weights',{}),head_strength)
        s=self.context_selector
        s.ranker=AlignedRanker(s.ranker,self.features,self.export_head,model.get('rank_models',{}).get(rank_variant,{}),rank_strength)
        s.context_fingerprint=fingerprint([s.context_fingerprint,self.p4_hash,head_strength,rank_strength,rank_variant])
        s.a123_models['p4_model']=self.p4_hash
        # Reference passes intentionally retain the verified P2 ranker.
    def analyze_sentence(self,text):return self.analyze_prepared(self._raw_schema_sentence(text))
    def _finish(self,out):
        out=super()._finish(out);out['tokenizer_version']=VERSION
        out['experiment'].update(id=VERSION,P4_head_strength=self.head_strength,P4_rank_strength=self.rank_strength,
            P4_rank_variant=self.rank_variant,P4_model_fingerprint=self.p4_hash,new_training_scope='SEPARATE_CONDITIONAL_VIEW_AND_EMITTED_OUTPUT_RANKING',
            original_P2_scoring_head_changed=False,P2_reference_passes_frozen=True,lexical_view_confidence_calibrated=False)
        if self.head_strength:
            for i,t in enumerate(out['tokens']):
                p=t.get('context_decision',{}).get('preferred_analysis');scores=self.export_head.token(out['tokens'],i)
                best=scores[p['analysis_id']] if p else None
                t['lexical_decision'].update(preferred_view=copy.deepcopy(best['view']) if best else None,
                    view_margin=best['view_margin'] if best else None,score=best['score'] if best else None,
                    calibrated_confidence=False)
        if self.p4_a2 is not None:
            apply_a2(out,self.p4_a2)
            for t in out['tokens']:t['lexical_decision']['native_model_separated']=t.get('decision_layers',{}).get('A2',{}).get('accepted',False)
        return out


class Codec(P2Codec):
    def __init__(self,policy='selective',**kwargs):
        super().__init__(1.,policy=policy);self.native=LazyNative(kwargs)
    def encode_from_analysis(self,out,policy=None):
        if out.get('tokenizer_version')!=VERSION:raise ValueError('P4_CODEC_REQUIRES_P4_OUTPUT')
        encoded=super().encode_from_analysis({**out,'tokenizer_version':P2_VERSION},policy)
        encoded['P4_configuration']={k:out['experiment'][k] for k in ('P4_head_strength','P4_rank_strength','P4_rank_variant')}
        return encoded


class LazyNative:
    def __init__(self,kwargs):self.kwargs=kwargs;self.runtime=None
    def analyze_sentence(self,text):
        if self.runtime is None:self.runtime=Tokenizer(**self.kwargs)
        return self.runtime.analyze_sentence(text)


def load_selected(with_a2=True):
    s=json.loads((ROOT/'results_layers_p4/selection.json').read_text(encoding='utf-8'))
    if s['model_sha256']!=json.loads(META.read_text(encoding='utf-8'))['sha256']:raise ValueError('P4_SELECTION_MODEL_CHANGED')
    return Tokenizer(**s['configuration'],a2=s.get('A2_config') if with_a2 else None)
