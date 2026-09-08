"""Licensed mI PART->AUX n-gram alignment; native labels and IDs stay intact."""
import hashlib
from pathlib import Path
from s06e_p2_policy import Tokenizer as PolicyTokenizer,Codec as PolicyCodec

QUESTION_IDS=frozenset({'R1V2:ZL:16044','R1V2:ZL:16091','R1V2:ZL:16427','R1V2:ZL:16798'})


class QuestionNgram:
    def __init__(self,base): self.base=base
    def __getattr__(self,name): return getattr(self.base,name)
    @staticmethod
    def tag(tag):
        if tag[0]!='PART': return tag
        if not tag[1].startswith('PART|'): raise ValueError('P2_Q_BAD_MORPH_SIGNATURE')
        return ('AUX','AUX'+tag[1][4:])
    def transition(self,a,b,c):
        return self.base.transition(*(self.tag(t) for t in (a,b,c)))
    def logp(self,channel,a,b,c):
        def mapped(x):
            if channel=='pos': return 'AUX' if x=='PART' else x
            if channel=='morph': return 'AUX'+x[4:] if x.startswith('PART|') else x
            return x
        return self.base.logp(channel,*(mapped(t) for t in (a,b,c)))
    def manifest(self):
        return {**self.base.manifest(),'question_alignment':'LICENSED_mI_PART_TO_TRAIN_AUX',
                'new_fit':False,'native_candidate_tags_rewritten':False,
                'alignment_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


class Tokenizer(PolicyTokenizer):
    def __init__(self,strength=1.,head_path=None,ranker_path=None):
        super().__init__(strength,head_path,ranker_path)
        entries=[e for e in self.analyzer.lexicon.entries if e.pos=='PART']
        if {e.id for e in entries}!=QUESTION_IDS or any(e.lemma!='mi' or 'R1Question' not in e.attrs for e in entries):
            raise ValueError('P2_Q_LICENSE_SET_CHANGED')
        shared=QuestionNgram(self.context_selector.ngram)
        def install(s):
            s.ngram=shared
            for attr in ('reference_selector','reference_ua'):
                child=getattr(s,attr,None)
                if child is not None: install(child)
        install(self.context_selector)
    def _raw_schema_sentence(self,text):
        out=super()._raw_schema_sentence(text)
        for t in out['tokens']:
            for a in t['analysis']['analyses']:
                if a['output_pos']=='PART' and a['lexeme_id'] not in QUESTION_IDS:
                    raise ValueError('P2_Q_UNLICENSED_PART_ANALYSIS')
        return out
    def _finish(self,out):
        out=super()._finish(out)
        out['experiment']['question_ngram_alignment']=True
        out['experiment']['question_alignment_scope']='mI_LICENSED_LEXEMES_ONLY'
        return out


class LazyNative:
    def __init__(self,strength,head_path,ranker_path): self.args=(strength,head_path,ranker_path); self.runtime=None
    def analyze_sentence(self,text):
        if self.runtime is None: self.runtime=Tokenizer(*self.args)
        return self.runtime.analyze_sentence(text)


class Codec(PolicyCodec):
    def __init__(self,strength=1.,head_path=None,ranker_path=None,policy='selective'):
        super().__init__(strength,head_path,ranker_path,policy)
        self.native=LazyNative(strength,head_path,ranker_path)
    def manifest(self): return {**super().manifest(),'question_ngram_alignment':True}
    def encode_from_analysis(self,out,policy=None):
        if not out.get('experiment',{}).get('question_ngram_alignment'):
            raise ValueError('P2_Q_CODEC_REQUIRES_ALIGNED_OUTPUT')
        return super().encode_from_analysis(out,policy)
