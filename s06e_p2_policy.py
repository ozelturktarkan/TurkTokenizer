"""Explicit UD_IMST representation policy; the same P1 candidate inventory."""
import hashlib
import json
from pathlib import Path
from bootstrap import ROOT
from s06e_p2 import Tokenizer as MixedTokenizer, SCHEMA_VERSION, E05_SHA256
from s06e_p2bpe import Tokenizer as MixedCodec
from r5.engine import fingerprint


class Tokenizer(MixedTokenizer):
    def __init__(self,strength=0.,head_path=None,ranker_path=None):
        meta=json.loads((ROOT/'results_lexical_p2/policy-imst/model-location.json').read_text(encoding='utf-8'))
        raw=Path(head_path or meta['path']).read_bytes(); sha=hashlib.sha256(raw).hexdigest()
        if sha!=meta['sha256']: raise ValueError('P2_POLICY_HEAD_HASH_MISMATCH')
        model=json.loads(raw)
        if (model.get('export_policy'),model.get('schema'),model.get('E05_sha256'))!=('UD_IMST',SCHEMA_VERSION,E05_SHA256):
            raise ValueError('P2_POLICY_SCHEMA_MISMATCH')
        # Keep the tested P2 computation and substitute only a verified head.
        super().__init__(strength,ranker_path=ranker_path)
        self.head.model=model; self.head.weights=model['weights']; self.head.sha256=sha
        self.head.tokens=None; self.head.cache={}
        def update(s):
            if getattr(getattr(s,'ranker',None),'head',None) is self.head:
                s.context_fingerprint=fingerprint([s.context_fingerprint,sha,'UD_IMST'])
            for attr in ('reference_selector','reference_ua'):
                child=getattr(s,attr,None)
                if child is not None: update(child)
        update(self.context_selector)
        self.context_selector.a123_models['p2_head.json']=sha
    def _finish(self,out):
        out=super()._finish(out); out['experiment']['export_policy']='UD_IMST'
        out['experiment']['head_training_source']='IMST_TRAIN_ONLY'
        return out
    def analyze_word(self,word,n_best=None):
        out=super().analyze_word(word,n_best)
        out['analysis_schema']['export_policy']='UD_IMST'
        return out


class LazyNative:
    def __init__(self,strength,head_path,ranker_path): self.args=(strength,head_path,ranker_path); self.runtime=None
    def analyze_sentence(self,text):
        if self.runtime is None: self.runtime=Tokenizer(*self.args)
        return self.runtime.analyze_sentence(text)


class Codec(MixedCodec):
    def __init__(self,strength=0.,head_path=None,ranker_path=None,policy='selective'):
        super().__init__(strength,ranker_path=ranker_path,policy=policy)
        self.native=LazyNative(strength,head_path,ranker_path)
    def manifest(self): return {**super().manifest(),'export_policy':'UD_IMST'}
    def encode_from_analysis(self,out,policy=None):
        if out.get('experiment',{}).get('export_policy')!='UD_IMST':
            raise ValueError('P2_POLICY_CODEC_REQUIRES_IMST_OUTPUT')
        encoded=super().encode_from_analysis(out,policy); encoded['export_policy']='UD_IMST'
        return encoded
