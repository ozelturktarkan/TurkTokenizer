"""Trace-backed lexical views; never rewrite native candidates or token IDs."""
import hashlib
import json
from functools import lru_cache

import bootstrap
from bootstrap import ROOT
from r5.engine import DERIV_CLASSES, fingerprint
from r5.lexicon import lower
from analysis_schema_s06e import validate_analysis

VERSION = 'S06E-P2-LEXICAL-VIEWS-1'


class LexicalViews:
    def __init__(self, analyzer):
        self.rows = analyzer.rows
        self.lexemes = {e.id: e for e in analyzer.lexicon.entries}
        self.unvoiced = {}
        for rid, row in self.rows.items():
            s = row.get('surface') or ''
            if s.endswith('ğ') and any(r.get('surface') == s[:-1] + 'k' and
                    r['class_tag'] == row['class_tag'] and r['morpheme_ids'] == row['morpheme_ids']
                    for r in self.rows.values()):
                self.unvoiced[rid] = s[:-1] + 'k'
        self.cache = {}

    def options(self, a):
        aid = a['analysis_id']
        if aid in self.cache:
            return self.cache[aid]
        validate_analysis(a, self.rows)
        candidates = {}
        def add(lemma, pos, kind, boundary=-1):
            if not lemma or pos not in {'NOUN','PROPN','PRON','ADJ','ADV','VERB','AUX','NUM','PART','DET','ADP','CCONJ','SCONJ','INTJ','X'}:
                return
            k = (lower(lemma), pos)
            if k in candidates:
                return
            v = {'lemma': k[0], 'output_pos': pos, 'features': dict(a['features']),
                 'kind': kind, 'boundary': boundary, 'analysis_id': aid,
                 'root_lemma': a['lemma'], 'root_pos': a['root_pos']}
            v['view_id'] = fingerprint([VERSION, aid, k])[:24]
            candidates[k] = v
        add(a['lemma'], a['output_pos'], 'ROOT_NATIVE')
        lexical = [(i, self.rows[rid]) for i, rid in enumerate(a['record_ids'])
                   if self.rows[rid]['class_tag'] in DERIV_CLASSES | {'ctE','atE'}
                   or a['morpheme_ids'][i] in {'VN_MA','VN_MAK','VN_IS'}]
        if not lexical and a['root_pos'] in {'ADJ','NUM'} and a['output_pos'] == 'NOUN':
            add(a['lemma'], a['root_pos'], 'ROOT_LEXICAL_POS')
        if a['features'].get('VerbForm') == 'Part' and a['output_pos'] == 'NOUN':
            add(a['lemma'], 'ADJ', 'PARTICIPIAL_MODIFIER')
        entry = self.lexemes.get(a.get('lexeme_id'))
        if entry and 'R1Question' in entry.attrs and a['root_pos'] == 'PART':
            add('mi', 'AUX', 'QUESTION_AUX')
        if entry and entry.secondary == 'Abbrv':
            add(a['lemma'], 'NOUN', 'ABBREVIATION_NOUN')
        for i, row in lexical:
            step = a['realization_trace'][i]
            lemma = step['after']
            if row['id'] in self.unvoiced:
                lemma = step['realized_stem'] + self.unvoiced[row['id']]
            # The last lexical boundary supplies the lexical lemma. Earlier
            # boundaries remain available for voice/derivation conventions.
            add(lemma, a['output_pos'], 'DERIVED_NATIVE_POS', i)
            if i == lexical[-1][0] and a['output_pos'] == 'NOUN' and not any(
                    m.startswith(('PART_','CONV_')) for m in a['morpheme_ids'][i+1:]):
                for pos in row['output_pos']:
                    if pos in {'ADJ','NUM'}:
                        add(lemma, pos, 'DERIVED_LEXICAL_POS', i)
        result = tuple(candidates.values())
        self.cache[aid] = result
        return result

    def schema(self, a):
        views = self.options(a)
        return {'schema_version': VERSION, 'analysis_id': a['analysis_id'],
                'root_lemma': a['lemma'], 'root_pos': a['root_pos'],
                'native_output_pos': a['output_pos'], 'native_features': dict(a['features']),
                'lexical_views': list(views), 'native_candidate_rewritten': False,
                'boundary_source': 'EXECUTABLE_REALIZATION_TRACE_AND_PINNED_REGISTRY',
                'full_feature_scope_adjudicated': False}


def view_features(tokens, index, a, v):
    """Observable context only. No selected neighbors or source labels."""
    raw = tokens[index]['raw']; word = lower(raw); f = a['features']; pos = v['output_pos']
    result = {}
    def add(*x): result[json.dumps(x, ensure_ascii=False, separators=(',',':'))] = 1.
    add('BIAS', v['kind']); add('POS', pos); add('ROOT_VIEW', a['root_pos'], a['output_pos'], pos)
    add('LEMMA_VIEW', v['lemma'], pos); add('WORD_VIEW', word, v['lemma'], pos)
    add('KIND_POS', v['kind'], pos); add('CAP', raw[:1].isupper(), pos)
    add('WHOLE', word == v['lemma'], pos); add('PATH', *a['morpheme_ids'], pos, v['kind'])
    for mid in a['morpheme_ids']: add('MID_VIEW', mid, pos, v['kind'])
    for k in ('Case','Number','VerbForm','Polarity','Person','Person[psor]','Number[psor]','Voice'):
        add('FEAT_VIEW', k, f.get(k,'-'), pos, v['kind'])
    for size in (2,3,4):
        if len(word) >= size: add('END_VIEW', word[-size:], pos, v['kind'])
    from r5.relations import HARD
    for off in (-2,-1,1,2):
        j=index+off; lo,hi=sorted((index,j))
        if j<0 or j>=len(tokens) or any(tokens[k]['raw'] in HARD for k in range(max(0,lo),min(len(tokens),hi+1)) if k!=index):
            add('BOUNDARY', off, pos); continue
        add('NEIGHBOR', off, lower(tokens[j]['raw']), pos)
        if abs(off)==1:
            add('NEIGHBOR_LEMMA',off,lower(tokens[j]['raw']),v['lemma'],pos)
    return result


def view_matches(v, gold, strict=False, explicit_copula=False, native=None):
    from common import canonical_pos
    if not gold or lower(v['lemma']) != lower(gold['lemma']) or v['output_pos'] not in canonical_pos(gold):
        return False
    if not strict: return True
    f=v['features']; gf=gold.get('feats',{})
    for k in ('VerbForm','Polarity','Voice','Person[psor]','Number[psor]'):
        if k in gf and f.get(k)!=gf[k]: return False
    for k, default in (('Case','Nom'),('Number','Sing'),('Person','3')):
        if k in gf and f.get(k,default)!=gf[k]: return False
    if explicit_copula and not any(m.startswith('COP_') for m in native['morpheme_ids']): return False
    return True
