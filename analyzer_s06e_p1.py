"""P1: phonological context repairs over frozen R5, without surface rewriting."""
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from analyzer_s06e_r5 import R5Analyzer
from bootstrap import ROOT, UPSTREAM
from r2_analyzer import LETTER_NAMES
from r5.engine import fingerprint
from r5.lexicon import VOWELS, lower, phonetic, last_vowel

VERSION = 'S06E-E05-P1-v0.1.0'
ARMS = ('baseline', 'circumflex', 'pronunciation', 'combined')
DATA = ROOT / 'data/s06e-p1/pronunciations.json'


class PhonologyAnalyzer(R5Analyzer):
    def __init__(self, arm='combined', **kwargs):
        if arm not in ARMS:
            raise ValueError('P1_UNKNOWN_ARM')
        super().__init__(**kwargs)
        self.p1_arm = arm
        self.p1_circumflex = arm in ('circumflex', 'combined')
        self.p1_pronunciation = arm in ('pronunciation', 'combined')
        self.p1_source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.p1_metadata_sha256 = hashlib.sha256(DATA.read_bytes()).hexdigest()
        self.pronunciation_sources = {}
        if self.p1_pronunciation:
            self._install_pronunciations()

    def _install_pronunciations(self):
        data = json.loads(DATA.read_text(encoding='utf-8'))
        if data['format'] != 'S06E_P1_PRONUNCIATION_METADATA_1':
            raise ValueError('P1_METADATA_FORMAT')
        source = (UPSTREAM / 'base/data/lexicon-combined.dict').read_text(encoding='utf-8').splitlines()
        updates = {}
        for e in self.lexicon.entries:
            # Existing explicit Pr and existing abbreviation readings are usable
            # at every phonological boundary, including after zero morphemes.
            md = {} if e.id.startswith('S04LEX:') else dict(re.findall(
                r'(\w+):([^;\]]+)', source[e.source_line - 1]))
            if 'Pr' in md:
                self.pronunciation_sources[e.id] = {'kind': 'PINNED_EXPLICIT_PR', 'line': e.source_line}
            elif e.secondary == 'Abbrv':
                self.pronunciation_sources[e.id] = {'kind': 'INHERITED_ABBREVIATION_READING', 'line': e.source_line}
        by_id = {e.id: e for e in self.lexicon.entries}
        for row in data['entries']:
            e = by_id[row['lexeme_id']]
            if (e.lemma, e.pos, e.pronunciation) != (row['lemma'], row['pos'], row['expected_pronunciation']):
                raise ValueError('P1_METADATA_BASE_CHANGED:' + e.id)
            if e.id in updates:
                raise ValueError('P1_DUPLICATE_METADATA')
            if row.get('reading_mode') == 'TURKISH_LETTER_NAMES':
                if e.secondary != 'Abbrv' or not all(c in LETTER_NAMES for c in e.stem):
                    raise ValueError('P1_UNLICENSED_LETTER_READING')
                pron = ''.join(LETTER_NAMES[c] for c in e.stem)
            else:
                pron = lower(row['pronunciation'])
            if not pron.isalpha() or not last_vowel(pron):
                raise ValueError('P1_INVALID_PRONUNCIATION')
            updates[e.id] = replace(e, pronunciation=pron)
            self.pronunciation_sources[e.id] = {'kind': 'REVIEWED_METADATA', **row}
        # Keep lexical IDs, all original seed aliases and all non-phonetic fields.
        self.lexicon.entries = [updates.get(e.id, e) for e in self.lexicon.entries]
        for attr in ('by_stem', 'seed_index'):
            old = getattr(self.lexicon, attr)
            setattr(self.lexicon, attr, defaultdict(list, {
                k: [updates.get(e.id, e) for e in values] for k, values in old.items()}))
        self.lexicon.sha256 = fingerprint([self.lexicon.sha256, self.p1_metadata_sha256])

    def _context(self, n, e, r, mid, s, target):
        # The spelling, search prefix and realization trace stay untouched.
        # Circumflex normalization is a same-length phonetic view of NFC text.
        context_stem = phonetic(s) if self.p1_circumflex else s
        ctx = super()._context(n, e, r, mid, context_stem, target)
        if self.p1_pronunciation and e.id in self.pronunciation_sources and s.startswith(e.stem):
            # Append realized suffixes: keep pronunciation through zero/consonant
            # suffixes, then let a realized suffix vowel determine subsequent harmony.
            spoken = phonetic(e.pronunciation + s[len(e.stem):])
            vowel = last_vowel(spoken)
            if 'InverseHarmony' in e.attrs and not any(
                    any(c in VOWELS for c in self.rows[rid]['surface']) for rid in n.ids):
                vowel = {'a': 'e', 'ı': 'i', 'o': 'ö', 'u': 'ü'}.get(vowel, vowel)
            ctx.update(last_vowel=vowel, last_segment='VOWEL' if spoken[-1] in VOWELS else 'CONSONANT',
                       last_voiceless=spoken[-1] in 'fstkçşhp')
        return ctx

    def manifest(self):
        parent = super().manifest()
        return {**parent, 'engine_version': VERSION, 'phonology_arm': self.p1_arm,
                'phonology_source_sha256': self.p1_source_sha256,
                'pronunciation_metadata_sha256': self.p1_metadata_sha256,
                'pronunciation_lexemes': len(self.pronunciation_sources),
                'input_spelling_rewritten': False, 'lexical_ids_changed': False,
                'grammar_sha256': fingerprint([parent['grammar_sha256'], self.p1_source_sha256,
                                               self.p1_metadata_sha256, self.p1_arm])}
