import copy
import itertools
import unittest
from grammar_p3 import Grammar,QUESTION_IDS
from r5.sequence import decode,BOS,EOS


def a(lemma,pos,**features):
    return {'analysis_id':lemma+pos+str(features),'lexeme_id':next(iter(QUESTION_IDS)) if pos=='PART' else lemma,
            'lemma':lemma,'root_pos':pos,'output_pos':pos,'features':features,'morpheme_ids':[]}


class GrammarTests(unittest.TestCase):
    def setUp(self):self.g=Grammar({'güven|Act':{'Dat':12,'Abl':1}})
    def test_postposition_reading_and_case(self):
        noun=a('okul','NOUN',Case='Dat');adp=a('doğru','ADP');adj=a('doğru','ADJ')
        self.assertEqual(self.g.pair(self.g.tag(noun),self.g.tag(adp)),{'gov.adp_match':1.})
        self.assertNotIn('gov.adp_match',self.g.pair(self.g.tag(noun),self.g.tag(adj)))
        wrong=a('okul','NOUN',Case='Loc')
        self.assertEqual(self.g.pair(self.g.tag(wrong),self.g.tag(adp)),{'gov.adp_mismatch':1.})
    def test_possessor_is_not_subject(self):
        owner=a('sen','PRON',Case='Gen');poss=a('ev','NOUN',Person__unused='1')
        poss['features']['Person[psor]']='2'
        fs=self.g.pair(self.g.tag(owner),self.g.tag(poss))
        self.assertEqual(fs,{'agr.poss_match':1.})
        verb=a('bil','VERB',VerbForm='Fin',Person='1',Number='Sing')
        self.assertEqual(self.g.subject(self.g.unpack(self.g.tag(owner)),self.g.unpack(self.g.tag(verb))),{})
    def test_question_carrier_and_note_contrast(self):
        sen=self.g.tag(a('sen','PRON',Case='Nom'));verb=self.g.tag(a('gel','VERB',VerbForm='Fin',Person='3'))
        q=self.g.tag(a('mi','PART',VerbForm='Fin',Person='2',Number='Sing'))
        fs=dict(self.g.transition(sen,verb,q))
        self.assertIn('agr.question_carrier_match',fs);self.assertNotIn('agr.subject_mismatch',fs)
        note=self.g.tag(a('mi','NOUN',Case='Nom'))
        self.assertIn('agr.note_after_finite',dict(self.g.transition(sen,verb,note)))
    def test_third_person_number_is_not_hard_equality(self):
        pron=self.g.unpack(self.g.tag(a('onlar','PRON',Case='Nom',Number='Plur')))
        for number in ['Sing','Plur']:
            pred=self.g.unpack(self.g.tag(a('gel','VERB',VerbForm='Fin',Person='3',Number=number)))
            self.assertEqual(self.g.subject(pron,pred),{'agr.subject_match':1.})
    def test_observed_frame_does_not_reject_unknown(self):
        verb=self.g.unpack(self.g.tag(a('uydur','VERB',VerbForm='Fin')))
        head=self.g.unpack(self.g.tag(a('ev','NOUN',Case='Abl')))
        self.assertEqual(self.g.case_preference(verb,head),0.)
    def test_no_gold_or_selected_neighbour_input(self):
        tokens=[{'raw':'senin','analysis':{'analyses':[a('sen','PRON',Case='Gen')]}},
                {'raw':'evin','analysis':{'analyses':[a('ev','NOUN',Case='Nom')]}}]
        expected=self.g.local(tokens,1,tokens[1]['analysis']['analyses'][0])
        changed=copy.deepcopy(tokens)
        for t in changed:t.update(gold={'lemma':'invented'},good_ids=['wrong'],context_decision={'preferred_analysis':{'lemma':'wrong'}})
        self.assertEqual(expected,self.g.local(changed,1,changed[1]['analysis']['analyses'][0]))
    def test_rich_tag_DP_and_marginals_equal_bruteforce(self):
        words=[[a('sen','PRON',Case='Nom')],[a('gel','VERB',VerbForm='Fin',Person='2'),a('gel','NOUN')],
               [a('mi','PART',VerbForm='Fin'),a('mi','NOUN')]]
        domains=[[{'id':str(i)+':'+str(j),'score':.1*j,'tag':self.g.tag(x)} for j,x in enumerate(aa)] for i,aa in enumerate(words)]
        def score(a,b,c):return sum(v*(2. if 'question' in k else -.5) for k,v in self.g.transition(a,b,c))
        paths=[]
        for items in itertools.product(*domains):
            tags=[BOS,BOS]+[x['tag'] for x in items]+[EOS]
            total=sum(x['score'] for x in items)+sum(score(*tags[j-2:j+1]) for j in range(2,len(tags)))
            paths.append((total,tuple(x['id'] for x in items)))
        paths.sort(key=lambda x:(-x[0],x[1]));got=decode(domains,score)
        self.assertAlmostEqual(got['score'],paths[0][0]);self.assertEqual(got['path'],paths[0][1])
        for i,domain in enumerate(domains):
            for x in domain:self.assertAlmostEqual(got['marginals'][i][x['id']],max(s for s,p in paths if p[i]==x['id']))


if __name__=='__main__':unittest.main()
