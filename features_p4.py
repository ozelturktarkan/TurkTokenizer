"""Observable representation features shared by separately fitted heads."""
import json
import collections
from analysis_schema_p2 import view_features,view_matches
from grammar_p3 import Grammar
from common import lower
from r5.relations import HARD

VERSION='S06E-P4-TWO-LAYER-FEATURES-1'


def emitted_positives(tokens,i,gold,explicit_copula,head):
    scores=head.token(tokens,i)
    return {a['analysis_id'] for a in tokens[i]['analysis']['analyses']
            if view_matches(scores[a['analysis_id']]['view'],gold,True,explicit_copula,a)}


class Features:
    def __init__(self,frames=None):
        self.grammar=Grammar(frames);self.tokens=None;self.stats={};self.cache={}
    def reset(self,tokens):
        if self.tokens is not tokens:self.tokens=tokens;self.stats={};self.cache={}
    def neighbour(self,tokens,i):
        self.reset(tokens)
        if i not in self.stats:
            variants={(a['output_pos'],a['features'].get('Case','Nom'),a['features'].get('VerbForm',''),
                       a['features'].get('Person',''),a['features'].get('Person[psor]','')) for a in tokens[i]['analysis']['analyses']}
            counts=collections.Counter()
            for pos,case,vf,person,psor in variants:
                for name,value in [('POS',pos),('POS_CASE',pos+':'+case),('POS_VF',pos+':'+vf),
                                   ('PERSON',person),('PSOR',psor)]:
                    if value:counts[(name,value)]+=1./len(variants)
            self.stats[i]=dict(counts)
        return self.stats[i]
    def view(self,tokens,i,a,v):
        self.reset(tokens);key=(i,a['analysis_id'],v['view_id'])
        if key in self.cache:return self.cache[key]
        result={'OLD:'+k:x for k,x in view_features(tokens,i,a,v).items()};pos=v['output_pos'];kind=v['kind'];f=v['features']
        def add(key,value=1.):result[json.dumps(key,ensure_ascii=False,separators=(',',':'))]=value
        add(['REP',pos,kind,a['root_pos'],a['output_pos']])
        add(['BOUNDARY_DEPTH',pos,kind],(v['boundary']+1)/max(1,len(a['morpheme_ids'])))
        for field in ('Case','VerbForm','Person','Number','Person[psor]','Number[psor]','Voice','Polarity'):
            add(['OUTPUT_FEATURE',pos,kind,field,f.get(field,'-')])
        for off in (-3,-2,-1,1,2,3):
            j=i+off;lo,hi=sorted((i,j))
            if j<0 or j>=len(tokens) or any(tokens[k]['raw'] in HARD for k in range(max(0,lo),min(len(tokens),hi+1)) if k!=i):
                add(['REP_BOUNDARY',off,pos,kind]);continue
            for (field,value),fraction in self.neighbour(tokens,j).items():
                add(['POSSIBLE_NEIGHBOUR',off,pos,field,value],fraction)
                if abs(off)==1:add(['POSSIBLE_NEIGHBOUR_KIND',off,kind,pos,field,value],fraction)
        for k,value in self.grammar.local(tokens,i,a).items():add(['GRAMMAR',pos,kind,k],value)
        self.cache[key]=result;return result
    def rank(self,tokens,i,a,v):
        result=dict(self.view(tokens,i,a,v));pos=v['output_pos']
        def add(key,value=1.):result[json.dumps(key,ensure_ascii=False,separators=(',',':'))]=value
        add(['NATIVE_PATH',pos,*a['morpheme_ids']]);add(['NATIVE_ROOT',lower(a['lemma']),a['output_pos'],pos])
        for mid in a['morpheme_ids']:add(['NATIVE_MORPHEME',mid,pos])
        add(['PATH_LENGTH',pos],len(a['morpheme_ids'])/5.)
        return result
