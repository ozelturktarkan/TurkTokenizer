"""Observable grammar features; bound factors use only the chosen analyses.

No candidate deletion, guessed dependency labels or required overt arguments.
TRAIN-derived case distributions are preferences, not exhaustive valency.
"""
import functools
import json
import math
from pathlib import Path
from analysis_schema_s06e import signature
from common import lower
from agreement_s06e_r3 import referent

VERSION='S06E-P3-GRAMMAR-1'
QUESTION_IDS=frozenset({'R1V2:ZL:16044','R1V2:ZL:16091','R1V2:ZL:16427','R1V2:ZL:16798'})
PERSONAL=frozenset({'ben','sen','o','biz','siz','onlar'})
NOMINAL=frozenset({'NOUN','PROPN','PRON'})
# These declarations are soft, reading-dependent features, never filters.
ADP_CASES={'göre':('Dat',),'rağmen':('Dat',),'karşı':('Dat',),'doğru':('Dat',),
           'dek':('Dat',),'değin':('Dat',),'itibaren':('Abl',),'dolayı':('Abl',),
           'ötürü':('Abl',),'beri':('Abl',),'önce':('Abl',),'sonra':('Abl',)}
CHANNELS=('local_government','local_agreement',
          'gov.adp_match','gov.adp_mismatch','gov.verb_case_left','gov.verb_case_right',
          'agr.poss_match','agr.poss_mismatch','agr.subject_match','agr.subject_mismatch',
          'agr.number12_match','agr.number12_mismatch','agr.finite_question','agr.note_after_finite',
          'agr.question_finite','agr.note_before_finite','agr.question_carrier_match',
          'agr.question_carrier_mismatch','agr.emphatic_question',
          'plan.gov.adp_match','plan.gov.adp_mismatch','plan.gov.verb_case',
          'plan.agr.poss_match','plan.agr.poss_mismatch','plan.agr.subject_match','plan.agr.subject_mismatch')


def family(name):
    return 'government' if 'gov' in name else 'agreement'


def active(name,arm):
    return arm=='combined' or family(name)==arm


class Grammar:
    def __init__(self,frame_counts=None):
        self.frames=frame_counts or {}
        self._tokens=None;self._unaries={}

    @staticmethod
    def tag(a,raw=''):
        f=a['features']; ref=referent(a); pos=a['output_pos']
        base=signature(pos,f)
        # Lemma and feature scope are kept; IDs are not needed to merge tags
        # that have exactly the same future grammar effects.
        info=(lower(a['lemma']),a['root_pos'],f.get('Case','Nom'),f.get('VerbForm',''),
              f.get('Person',''),f.get('Number',''),f.get('Person[psor]',''),
              f.get('Number[psor]',''),f.get('Voice','Act'),
              a.get('lexeme_id') in QUESTION_IDS, ref[0] if ref else '',ref[1] if ref else '',
              any(m.startswith(('COP_','AGR_')) for m in a['morpheme_ids']),
              any(m.startswith(('A_NESS','N_AGENT','VN_','REL_KI')) for m in a['morpheme_ids']))
        return base+(info,)

    @staticmethod
    def unpack(t):
        if len(t)<3:return None
        z=t[2]
        return dict(pos=t[0],lemma=z[0],root_pos=z[1],case=z[2],vf=z[3],person=z[4],number=z[5],
                    psor=z[6],npsor=z[7],voice=z[8],question=z[9],refperson=z[10],refnumber=z[11],
                    agreement_marked=z[12],nominal_derivation=z[13])

    @staticmethod
    def finite(t):
        return bool(t and (t['vf']=='Fin' or (t['question'] and t['agreement_marked'])))

    @staticmethod
    def nominal(t):
        return bool(t and t['pos'] in NOMINAL and t['vf'] not in {'Fin','Conv'})

    @staticmethod
    def adp_expected(t,head):
        if t['pos']!='ADP':return ()
        if t['lemma'] in {'gibi','için'}:
            return ('Gen',) if head['pos']=='PRON' and head['lemma'] in PERSONAL else ('Nom',)
        return ADP_CASES.get(t['lemma'],())

    def case_preference(self,verb,head):
        if not verb or verb['root_pos']!='VERB' or verb['pos']!='VERB' or verb['nominal_derivation']:return 0.
        counts=self.frames.get(verb['lemma']+'|'+verb['voice'],{})
        n=sum(counts.values())
        if n<3:return 0.
        # Nominative is ambiguous between subject and bare object; its absence
        # from observed object/oblique dependents is not negative evidence.
        case=head['case']
        if case=='Nom':return 0.
        p=(counts.get(case,0)+.5)/(n+3.)
        return max(-2.,min(2.,math.log(p/(1./6.))))

    def pair(self,left,right):
        b,c=self.unpack(left),self.unpack(right);out={}
        if not b or not c:return out
        if self.nominal(b):
            expected=self.adp_expected(c,b)
            if expected:out['gov.adp_'+('match' if b['case'] in expected else 'mismatch')]=1.
            v=self.case_preference(c,b)
            if v:out['gov.verb_case_left']=v
        if self.nominal(c):
            v=self.case_preference(b,c)
            if v:out['gov.verb_case_right']=v
            if self.nominal(b) and b['case']=='Gen' and b['refperson'] and c['psor']:
                out['agr.poss_'+('match' if b['refperson']==c['psor'] else 'mismatch')]=1.
        if self.finite(b):
            if c['question']:out['agr.finite_question']=1.
            elif c['pos']=='NOUN' and c['lemma']=='mi':out['agr.note_after_finite']=1.
        if self.finite(c):
            if b['question']:out['agr.question_finite']=1.
            elif b['pos']=='NOUN' and b['lemma']=='mi':out['agr.note_before_finite']=1.
        return out

    @staticmethod
    def subject(subject,predicate,prefix='agr.'):
        out={}
        if not subject or not predicate:return out
        if subject['pos']!='PRON' or subject['case']!='Nom' or not subject['refperson']:return out
        if not Grammar.finite(predicate) or not predicate['person']:return out
        match=subject['refperson']==predicate['person']
        out[prefix+'subject_'+('match' if match else 'mismatch')]=1.
        # Third-person and coordinated number equality is deliberately absent.
        if match and predicate['person'] in {'1','2'} and subject['refnumber'] and predicate['number']:
            out[prefix+'number12_'+('match' if subject['refnumber']==predicate['number'] else 'mismatch')]=1.
        return out

    @functools.lru_cache(maxsize=100000)
    def transition(self,a,b,c):
        out=self.pair(b,c);aa,bb,cc=map(self.unpack,(a,b,c))
        # Charge subject agreement one step later so a following question
        # carrier can supply person without comparing it to a bare 3sg verb.
        if aa and bb:
            if cc and cc['question']:
                if cc['person'] and aa['pos']=='PRON' and aa['case']=='Nom' and aa['refperson']:
                    out['agr.question_carrier_'+('match' if aa['refperson']==cc['person'] else 'mismatch')]=1.
            else:out.update(self.subject(aa,bb))
        # An adjacent postverbal subject is also a soft possibility.
        if bb and cc:out.update(self.subject(cc,bb))
        if aa and bb and cc:
            if bb['pos'] in {'ADJ','DET'} and self.nominal(aa) and self.nominal(cc) and aa['case']=='Gen' and aa['refperson'] and cc['psor']:
                out['agr.poss_'+('match' if aa['refperson']==cc['psor'] else 'mismatch')]=1.
            if aa['pos']=='ADJ' and cc['pos']=='ADJ' and aa['lemma']==cc['lemma'] and bb['question']:
                out['agr.emphatic_question']=1.
        return tuple(sorted(out.items()))

    def local(self,tokens,index,a):
        if self._tokens is not tokens:self._tokens=tokens;self._unaries={}
        aid=a['analysis_id'];key=(index,aid)
        if key in self._unaries:return self._unaries[key]
        this=self.tag(a); fs={}
        for off in (-1,1):
            j=index+off
            if not 0<=j<len(tokens):continue
            tags={self.tag(b) for b in tokens[j]['analysis']['analyses']}
            values=[]
            for other in tags:
                left,right=(other,this) if off<0 else (this,other)
                evidence=self.pair(left,right)
                evidence.update(self.subject(self.unpack(left),self.unpack(right)))
                evidence.update(self.subject(self.unpack(right),self.unpack(left)))
                values.append(evidence)
            for name in sorted({k for d in values for k in d}):
                numbers=[d.get(name,0.) for d in values]
                # Candidate-set evidence is explicitly existential/uncertain.
                # It does not assert that a neighbour's reading was selected.
                for stat,value in [('max',max(numbers)),('min',min(numbers))]:
                    if value:fs[json.dumps([family(name),off,stat,name],separators=(',',':'))]=value
        self._unaries[key]=fs
        return fs

    def plan(self,tokens,plan):
        lookup={i:next(a for a in tokens[i]['analysis']['analyses'] if a['analysis_id']==aid) for i,aid in plan['bindings'].items()}
        tags={i:self.unpack(self.tag(a)) for i,a in lookup.items()};fs={}
        def add(name,value=1.):fs[name]=fs.get(name,0.)+value
        for link in plan['links']:
            dep,head=tags[link['dependent']],tags[link['head']]
            if link['relation']=='case':
                expected=self.adp_expected(dep,head)
                if expected:add('plan.gov.adp_'+('match' if head['case'] in expected else 'mismatch'))
            elif link['relation']=='nmod:poss' and dep['refperson'] and head['psor']:
                add('plan.agr.poss_'+('match' if dep['refperson']==head['psor'] else 'mismatch'))
        for role in plan['roles']:
            pred,dep=tags[role['predicate']],tags[role['argument']]
            if role['relation'].startswith('nsubj'):
                # Existing planner decides whether this relation is in scope.
                for k,v in self.subject(dep,pred).items():
                    if 'subject_' in k:add('plan.'+k,v)
            elif role['relation'] in {'obj','obl:arg','obl'}:
                v=self.case_preference(pred,dep)
                if v:add('plan.gov.verb_case',v)
        return fs
