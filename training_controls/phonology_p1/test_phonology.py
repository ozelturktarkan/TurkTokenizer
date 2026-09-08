"""Contrasting legitimate and ill-formed paths, spelling, IDs and cache isolation."""
import copy
import unittest
import unicodedata
from dataclasses import replace

from analyzer_s06e_p1 import PhonologyAnalyzer
from analyzer_s06e_r5 import R5Analyzer

# Hand-specified paradigms, not generated from the implementation's conditions.
PAIRS = [
    ('vicahîye', 'vicahîe', 'vicahî', 'CASE_DAT'),
    ('zekâya', 'zekâa', 'zekâ', 'CASE_DAT'),
    ('rükûya', 'rükûa', 'rükû', 'CASE_DAT'),
    ('millîyim', 'millîim', 'millî', 'AGR_1_SING'),
    ('millîydi', 'millîdi', 'millî', 'COP_PAST'),
    ("Taylor'ın", "Taylor'un", 'taylor', 'CASE_GEN'),
    ("Taylor'a", "Taylor'e", 'taylor', 'CASE_DAT'),
    ("Taylor'ım", "Taylor'um", 'taylor', 'AGR_1_SING'),
    ("Taylor'ımız", "Taylor'umuz", 'taylor', 'POSS_1_PLUR'),
    ("Taylor'ıma", "Taylor'ıme", 'taylor', 'CASE_DAT'),
    ("İMKB'nin", "İMKB'in", 'imkb', 'CASE_GEN'),
    ("İMKB'ye", "İMKB'e", 'imkb', 'CASE_DAT'),
    ("İMKB'de", "İMKB'te", 'imkb', 'CASE_LOC'),
    ("İMKB'yim", "İMKB'im", 'imkb', 'AGR_1_SING'),
    ("TBMM'yim", "TBMM'yım", 'tbmm', 'AGR_1_SING'),
    ("TDK'den", "TDK'tan", 'tdk', 'CASE_ABL'),
    ("Abby'ye", "Abby'ya", 'abby', 'CASE_DAT'),
    ("Vodafone'a", "Vodafone'ya", 'vodafone', 'CASE_DAT'),
    ("Vodafone'um", "Vodafone'yim", 'vodafone', 'AGR_1_SING'),
    ("NATO'dan", "NATO'den", 'nato', 'CASE_ABL'),
    ("UNESCO'ya", "UNESCO'ye", 'unesco', 'CASE_DAT'),
    ("BOTAŞ'ın", "BOTAŞ'in", 'botaş', 'CASE_GEN'),
    ('hâli', 'hâlı', 'hâl', 'CASE_ACC'),
    ('kitaba', 'kitapa', 'kitap', 'CASE_DAT'),
    ('ağzı', 'ağzi', 'ağız', 'CASE_ACC'),
]


def matches(result, lemma, mid):
    return [a for a in result['analyses'] if a['lemma'] == lemma and mid in a['morpheme_ids']]


class PhonologyContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixed = PhonologyAnalyzer()
        cls.old = R5Analyzer()

    def test_contrasting_paradigms(self):
        for good, bad, lemma, mid in PAIRS:
            with self.subTest(good=good, bad=bad):
                yes, no = self.fixed.analyze(good), self.fixed.analyze(bad)
                self.assertTrue(yes['search_complete'] and no['search_complete'])
                self.assertTrue(matches(yes, lemma, mid))
                self.assertFalse(matches(no, lemma, mid))

    def test_zero_transitions_and_suffix_harmony(self):
        # Root reading must survive a zero COP and then yield to an overt vowel.
        for text in ["Taylor'ım", "TBMM'yim", "Vodafone'um"]:
            analyses = self.fixed.analyze(text)['analyses']
            self.assertTrue(any(a['morpheme_ids'] == ['COP_PRESENT', 'AGR_1_SING'] for a in analyses))
        for good, bad in [("Taylor'larım", "Taylor'lerim"), ("Abby'lerim", "Abby'larım")]:
            self.assertTrue(self.fixed.analyze(good)['analyses'])
            self.assertFalse(self.fixed.analyze(bad)['analyses'])

    def test_spelling_and_trace_preserved(self):
        for good, _, _, _ in PAIRS:
            r = self.fixed.analyze(good)
            self.assertEqual(r['raw'], good)
            for a in r['analyses']:
                for trace in a['realization_trace']:
                    self.assertEqual(trace['realized_stem'] + trace['suffix'], trace['after'])
                if a['realization_trace']:
                    self.assertEqual(a['realization_trace'][-1]['after'], a['surface'])
                for rid, mid in zip(a['record_ids'], a['morpheme_ids'], strict=True):
                    self.assertIn(mid, self.fixed.rows[rid]['morpheme_ids'])
        self.assertFalse(self.fixed.analyze('vicahiye')['analyses'])  # no silent deaccenting
        self.assertNotEqual({a['lemma'] for a in self.fixed.analyze('hâli')['analyses']},
                            {a['lemma'] for a in self.fixed.analyze('hali')['analyses']})

    def test_lexeme_ids_and_nonphonetic_fields_unchanged(self):
        old = {e.id: e for e in self.old.lexicon.entries}
        new = {e.id: e for e in self.fixed.lexicon.entries}
        self.assertEqual(old.keys(), new.keys())
        for key, e in old.items():
            self.assertEqual(e, replace(new[key], pronunciation=e.pronunciation))
        self.assertEqual(self.old.rows, self.fixed.rows)
        self.assertEqual(self.old.manifest()['candidate_search_limits'], self.fixed.manifest()['candidate_search_limits'])

    def test_unchanged_paths_keep_ids_and_full_content(self):
        for word in ['kitap', 'kitaba', 'geldim', 'ağzı', 'hâli', 'millîlik', 'bütün', 'hangisi', "NATO'dan", "BOTAŞ'ın"]:
            self.assertEqual(self.old.analyze(word)['analyses'], self.fixed.analyze(word)['analyses'], word)

    def test_known_vowel_drop_gap_is_not_claimed_fixed(self):
        # A duplicate historical ağız reading still licenses ağızı. This patch
        # does not repair that lexical gap or count its retention as correctness.
        old = self.old.analyze('ağızı')['analyses']
        self.assertTrue(old)
        self.assertEqual(old, self.fixed.analyze('ağızı')['analyses'])

    def test_unicode_and_cache_isolation(self):
        expected = copy.deepcopy(self.fixed.analyze('vicahîye')['analyses'])
        self.fixed.analyze('vicahîe')
        self.assertEqual(self.fixed.analyze('vicahîye')['analyses'], expected)
        self.assertEqual(self.fixed.analyze(unicodedata.normalize('NFD', 'vicahîye'))['analyses'], expected)
        self.assertEqual(self.fixed.analyze("Taylor'ın")['analyses'], self.fixed.analyze('Taylor’ın')['analyses'])
        self.assertFalse(self.fixed.analyze("taylor'ın")['analyses'])
        self.assertFalse(self.old.analyze('vicahîye')['analyses'])


if __name__ == '__main__':
    unittest.main()
