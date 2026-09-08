"""Opt-in P3 grammar residual with the same P1/P2 morphology and BPE IDs."""
import copy
import hashlib
import json
import math
import types
import functools
from pathlib import Path
from bootstrap import ROOT
from s06e_p2_policy import Tokenizer as P2Tokenizer,Codec as P2Codec
from s06e_p2 import VERSION as P2_VERSION
from s05_ua_features import UARanker
from r5.engine import fingerprint
from decisions_s06e import annotate
from s06e_a123 import annotate_features,apply_a2
from grammar_p3 import Grammar,CHANNELS,VERSION as GRAMMAR_VERSION,active

VERSION='S06E-P3-YONT-v0.1.0'
META=ROOT/'results_grammar_p3/model-location.json'


class LocalRanker(UARanker):
    def __init__(self,base,grammar,weights,theta):
        self.base=base;self.grammar=grammar;self.local_weights=weights;self.theta=theta
        self.model=base.model;self.weights=base.weights;self.segmenter=base.segmenter
    def parts(self,tokens,i,a):
        sums=[0.,0.]
        for k,v in self.grammar.local(tokens,i,a).items():
            j=0 if k.startswith('["government"') else 1
            sums[j]+=v*self.local_weights.get(k,0.)
        return sums
    def token(self,tokens,i):
        base=self.base.token(tokens,i)
        if not any(self.theta[:2]):return base
        scores={a['analysis_id']:base[a['analysis_id']]+sum(x*y for x,y in zip(self.parts(tokens,i,a),self.theta[:2]))
                for a in tokens[i]['analysis']['analyses']}
        peak=max(scores.values(),default=0.)
        return {k:v-peak for k,v in scores.items()}


class GrammarNgram:
    def __init__(self,base,grammar,theta,ngram_weight):
        self.base=base;self.grammar=grammar;self.theta=dict(zip(CHANNELS,theta));self.ngram_weight=ngram_weight
    def __getattr__(self,n):return getattr(self.base,n)
    def tag(self,a):return self.grammar.tag(a)
    @functools.lru_cache(maxsize=150000)
    def transition(self,a,b,c):
        extra=sum(self.theta.get(k,0.)*v for k,v in self.grammar.transition(a,b,c))
        return self.base.transition(a[:2],b[:2],c[:2])+extra/self.ngram_weight
    def manifest(self):
        return {**self.base.manifest(),'grammar_adapter':GRAMMAR_VERSION,'native_ngram_signatures_unchanged':True,
                'grammar_is_separate_score':True}


class GrammarPlanner:
    def __init__(self,base,grammar,theta,relation_weight):
        self.base=base;self.grammar=grammar;self.theta=dict(zip(CHANNELS,theta));self.relation_weight=relation_weight
    def __getattr__(self,n):return getattr(self.base,n)
    def plans(self,tokens,indices,*args):
        g=self.base.plans(tokens,indices,*args)
        if not any(v for k,v in self.theta.items() if k.startswith('plan.')):return g
        original={}
        for p in g['plans']+[p for d in g['support'].values() for p in d.values()]:
            key=json.dumps([p['frame_id'],p['bindings'],p['roles'],p['links']],sort_keys=True)
            original.setdefault(key,p)
        revised=[]
        for p in original.values():
            fs=self.grammar.plan(tokens,p);extra=sum(self.theta.get(k,0.)*v for k,v in fs.items())
            revised.append({**p,'score':p['score']+extra/self.relation_weight,
                            'p3_base_score':p['score'],'p3_features':fs,'p3_score_delta':extra})
        revised.sort(key=lambda p:(-self.base.relation_weight*p['score']-self.base.bound_score(p['bindings']),
                                   p['frame_id'],json.dumps(p['bindings'],sort_keys=True)))
        support={}
        for p in revised:
            for i,aid in p['bindings'].items():support.setdefault(i,{}).setdefault(aid,p)
        return {**g,'plans':revised[:8],'support':support,'p3_rescored_plans':len(revised),
                'p3_scope':'PARENT_RETAINED_PROPOSALS_ONLY'}
    def manifest(self):
        return {**self.base.manifest(),'P3_features':True,'prior_beam_pruning_reversed':False}


def grammar_apply(self,sentence):
    from decoder_p3 import decode_sentence
    self.audit=[];self.proposal_audit=[]
    self.reference=self.reference_selector.apply(copy.deepcopy(sentence)) if self.reference_selector else None
    self.ua_reference_output=self.reference_ua.apply(copy.deepcopy(sentence)) if self.reference_ua else None
    try:
        out=decode_sentence(self,sentence)
        out['ab04_view_evidence']={'arm':'S06E-'+self.s06e_arm,'weight':self.weight,'tokens':self.audit}
        out['ab04_repair']={'version':'S06E-1','pruning_completion_residual':True,'tau':self.tau,
            'reference_pass':'Q0' if self.reference_selector else None,'hard_reference_bindings':False,
            'final_shared_redecode':True,'weight':self.weight,'extra_fit':True}
        out['ab04_joint_proposals']={'version':'0.5.0','stage':self.stage,'audit':self.proposal_audit,
            'final_objective_changed':True,'unaries_counted_once':True,'ngram_in_proposal_priority':False,
            'copied_reference_bindings':False}
        return annotate_features(annotate(out,self),self)
    finally:
        self.reference=None;self.ua_reference_output=None


class Tokenizer(P2Tokenizer):
    def __init__(self,configuration='C0_P2',model_path=None,model=None,theta=None,arm=None,a2=None):
        super().__init__(strength=1.)
        supplied_model=model is not None
        if model is None:
            meta=json.loads(META.read_text(encoding='utf-8'))
            path=Path(model_path or meta['path']);contents=path.read_bytes()
            if hashlib.sha256(contents).hexdigest()!=meta['sha256']:raise ValueError('P3_MODEL_HASH_MISMATCH')
            model=json.loads(contents)
        if model['version']!=GRAMMAR_VERSION:raise ValueError('P3_GRAMMAR_SCHEMA')
        if model['P2_head_sha256']!=self.head.sha256:raise ValueError('P3_P2_BASE_CHANGED')
        if not supplied_model and configuration not in model.get('configurations',{}):
            raise ValueError('P3_UNKNOWN_CONFIGURATION')
        self.p3_model=model;self.p3_hash=fingerprint(model);self.p3_configuration=configuration;self.p3_a2=a2
        setting=model.get('configurations',{}).get(configuration,{})
        arm=arm or setting.get('arm','combined')
        theta=list(theta if theta is not None else setting.get('theta',[0.]*len(CHANNELS)))
        if len(theta)!=len(CHANNELS) or any(not math.isfinite(x) for x in theta):raise ValueError('P3_BAD_WEIGHTS')
        if arm not in {'government','agreement','combined'}:raise ValueError('P3_BAD_ARM')
        if any(x and not active(k,arm) for k,x in zip(CHANNELS,theta)):raise ValueError('P3_MASK_VIOLATION')
        self.p3_theta=theta;self.p3_arm=arm;self.grammar=Grammar(model.get('frame_counts',{}))
        local=model.get('local_models',{}).get(arm,{})
        self.p3_runtime_training_override=bool(supplied_model and configuration not in model.get('configurations',{}))
        def install(s):
            if isinstance(getattr(s,'ranker',None),UARanker):
                s.ranker=LocalRanker(s.ranker,self.grammar,local,theta)
                s.context_fingerprint=fingerprint([s.context_fingerprint,self.p3_hash,arm,theta])
                s.planner=GrammarPlanner(s.planner,self.grammar,theta,s.relation_weight)
                if any(x for k,x in zip(CHANNELS,theta) if k.startswith(('gov.','agr.'))):
                    s.ngram=GrammarNgram(s.ngram,self.grammar,theta,s.ngram_weight)
                    s.apply=types.MethodType(grammar_apply,s)
            for attr in ('reference_selector','reference_ua'):
                child=getattr(s,attr,None)
                if child is not None:install(child)
        install(self.context_selector)
        self.context_selector.a123_models['p3_grammar_model']=self.p3_hash

    def analyze_sentence(self,text):
        # One finish/calibration pass for both ordinary calls and cached replay.
        return self.analyze_prepared(self._raw_schema_sentence(text))

    def _finish(self,out):
        out=super()._finish(out);out['tokenizer_version']=VERSION
        out['experiment'].update(id=VERSION,grammar_version=GRAMMAR_VERSION,P3_configuration=self.p3_configuration,
            P3_arm=self.p3_arm,P3_weights=dict(zip(CHANNELS,self.p3_theta)),P3_model_fingerprint=self.p3_hash,
            new_training_scope='IMST_TRAIN_LOCAL_AND_BOUND_GRAMMAR',new_morphological_paths=False,
            old_five_channel_weights_frozen=True,zero_contribution=not any(self.p3_theta),
            pair_scope='ADJACENT_TRIPLES',plan_scope='PARENT_RETAINED_PARTIAL_PLANS',
            word_order_focus_package=False,lexical_view_head_changed=False)
        if self.p3_a2 is not None:
            apply_a2(out,self.p3_a2)
            for t in out['tokens']:
                t['lexical_decision']['native_model_separated']=t.get('decision_layers',{}).get('A2',{}).get('accepted',False)
                t['lexical_decision']['calibrated_confidence']=False
        return out


class Codec(P2Codec):
    def __init__(self,configuration='C0_P2',model_path=None,model=None,theta=None,arm=None,a2=None,policy='selective'):
        super().__init__(strength=1.,policy=policy)
        self._p3_args=dict(configuration=configuration,model_path=model_path,model=model,theta=theta,arm=arm,a2=a2)
        self.native=LazyNative(self._p3_args)
    def encode_from_analysis(self,out,policy=None):
        if out.get('tokenizer_version')!=VERSION:raise ValueError('P3_CODEC_REQUIRES_P3_OUTPUT')
        adjusted={**out,'tokenizer_version':P2_VERSION}
        encoded=super().encode_from_analysis(adjusted,policy)
        encoded['P3_configuration']=out['experiment']['P3_configuration']
        return encoded


class LazyNative:
    def __init__(self,kwargs):self.kwargs=kwargs;self.runtime=None
    def analyze_sentence(self,text):
        if self.runtime is None:self.runtime=Tokenizer(**self.kwargs)
        return self.runtime.analyze_sentence(text)


def load_selected(with_a2=True):
    selection=json.loads((ROOT/'results_grammar_p3/selection.json').read_text(encoding='utf-8'))
    return Tokenizer(selection['configuration'],a2=selection.get('A2_config') if with_a2 else None)
