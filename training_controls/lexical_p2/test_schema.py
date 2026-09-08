import copy
import unittest
from analyzer_s06e_p1 import PhonologyAnalyzer
from analysis_schema_p2 import LexicalViews, view_features, view_matches


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer=PhonologyAnalyzer('combined'); cls.views=LexicalViews(cls.analyzer)

    def analyses(self, word):
        return self.analyzer.analyze(word)['analyses']

    def test_derived_lemma_and_root_preserved(self):
        for word, root, lemma, pos in [('duygusal','duygu','duygusal','ADJ'),
                ('güzelliğinden','güzel','güzellik','NOUN'),
                ('işletmecilerinden','işletme','işletmeci','NOUN'),
                ('gerçekleştirilen','gerçek','gerçekleştir','NOUN')]:
            aa=self.analyses(word); old=copy.deepcopy(aa)
            vv=[v for a in aa for v in self.views.options(a) if a['lemma']==root]
            self.assertTrue(any((v['lemma'],v['output_pos'])==(lemma,pos) for v in vv), word)
            self.assertTrue(all(v['root_lemma']==root for v in vv)); self.assertEqual(aa,old)

    def test_no_arbitrary_inflection_as_lemma(self):
        aa=[a for a in self.analyses('evlerimizden') if a['lemma']=='ev' and
            a['morpheme_ids']==['NUMBER_PL','POSS_1_PLUR','CASE_ABL']]
        self.assertTrue(aa)
        self.assertEqual({v['lemma'] for a in aa for v in self.views.options(a)}, {'ev'})
        for a in aa:
            vv=self.views.options(a)
            self.assertEqual(len(vv),len({(v['lemma'],v['output_pos']) for v in vv}))

    def test_question_and_abbreviation_licenses(self):
        for word in ['mi','miyim','musun','mü']:
            aa=self.analyses(word)
            self.assertTrue(any(v['output_pos']=='AUX' for a in aa for v in self.views.options(a)))
            for a in aa:
                if a['root_pos']=='NOUN': self.assertFalse(any(v['output_pos']=='AUX' for v in self.views.options(a)))
        self.assertTrue(any(v['kind']=='ABBREVIATION_NOUN' for a in self.analyses('İMKB’nin') for v in self.views.options(a)))
        self.assertFalse(any(v['kind']=='ABBREVIATION_NOUN' for a in self.analyses('Taylor’ın') for v in self.views.options(a)))

    def test_nominal_origin_and_feature_strictness(self):
        aa=[a for a in self.analyses('kurnazı') if a['root_pos']=='ADJ']
        self.assertTrue(aa)
        self.assertTrue(any(v['output_pos']=='ADJ' for a in aa for v in self.views.options(a)))
        a=next(a for a in self.analyses('evleri') if a['features'].get('Case')=='Acc')
        v=self.views.options(a)[0]
        gold={'lemma':'ev','upos':'NOUN','feats':{'Case':'Nom','Number':'Plur'},'deprel':'nsubj'}
        self.assertTrue(view_matches(v,gold)); self.assertFalse(view_matches(v,gold,True))

    def test_no_label_or_neighbor_selection_leak(self):
        ts=[{'raw':w,'analysis':self.analyzer.analyze(w)} for w in ['Güzel','evleri','gördüm']]
        a=ts[1]['analysis']['analyses'][0]; v=self.views.options(a)[0]
        expected=view_features(ts,1,a,v)
        for t in ts:
            t['gold']={'lemma':'FAKE','upos':'X'}; t['good_ids']=['FAKE']
            t['context_decision']={'preferred_analysis':{'lemma':'FAKE'}}
            t['analysis']['analyses'].reverse()
        self.assertEqual(expected,view_features(ts,1,a,v))


if __name__=='__main__': unittest.main()
