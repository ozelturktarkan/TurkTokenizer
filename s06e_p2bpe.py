"""P2 native selection with the unchanged 224309-ID P1/R5 codec."""
from s06e_p1bpe import Tokenizer as P1Codec
from s06e_p1 import VERSION as P1_VERSION
from s06e_p2 import Tokenizer as Native, VERSION as NATIVE_VERSION

VERSION='S06E-E05-P2BPE-v0.1.0'


class LazyNative:
    def __init__(self,strength,head_path,ranker_path):
        self.args=(strength,head_path,ranker_path); self.runtime=None
    def analyze_sentence(self,text):
        if self.runtime is None: self.runtime=Native(*self.args)
        return self.runtime.analyze_sentence(text)


class Tokenizer(P1Codec):
    def __init__(self,strength=0.,head_path=None,ranker_path=None,policy='selective'):
        super().__init__('combined',ranker_path,policy)
        self.p2_strength=strength; self.native=LazyNative(strength,head_path,ranker_path)
    def manifest(self):
        return {**super().manifest(),'id':VERSION,'morphology_base':NATIVE_VERSION,
                'lexical_residual_strength':self.p2_strength,'historical_R5_ids_unchanged':True}
    def encode_from_analysis(self,out,policy=None):
        if out.get('tokenizer_version')!=NATIVE_VERSION or out.get('experiment',{}).get('residual_strength')!=self.p2_strength:
            raise ValueError('P2_CODEC_REQUIRES_MATCHING_OUTPUT')
        result=super().encode_from_analysis({**out,'tokenizer_version':P1_VERSION},policy)
        result['tokenizer_version']=VERSION
        return result
    def analyze_sentence(self,text,include_native=False):
        result=super().analyze_sentence(text,include_native); result['tokenizer_version']=VERSION
        return result
