"""Observable scoped evidence for possession, case and predicate person.

Candidate fractions preserve uncertainty. No selected neighbours, gold, document
IDs or memorized error surfaces are inputs. Evidence is soft, never a parser.
"""
import bootstrap
from r5.lexicon import lower
from r5.relations import HARD, COORD

VERSION = 'P7-SCOPED-FORMULAS-1'
FAMILIES = ('poss', 'case', 'person')
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'ADJ', 'NUM'}
PERSONAL = {'ben': ('1', 'Sing'), 'sen': ('2', 'Sing'), 'biz': ('1', 'Plur'),
            'siz': ('2', 'Plur'), 'o': ('3', 'Sing'), 'onlar': ('3', 'Plur')}


def tag(a):
    f = a['features']
    return (lower(a['lemma']), a['root_pos'], a['output_pos'], f.get('Case', 'Nom'),
            f.get('VerbForm', ''), f.get('Person', ''), f.get('Number', 'Sing'),
            f.get('Person[psor]', ''), f.get('Number[psor]', ''), f.get('Voice', 'Act'))


def referent(t):
    if t[1] == t[2] == 'PRON' and t[0] in PERSONAL:
        return PERSONAL[t[0]]
    if t[2] in {'NOUN', 'PROPN'} and t[4] != 'Fin':
        return '3', t[6]
    return None


class Formulas:
    def __init__(self, frames=None):
        self.frames = frames or {}
        self.tokens = None
        self.tags = []
        self.cache = {}

    def reset(self, tokens):
        if self.tokens is tokens:
            return
        self.tokens = tokens
        self.tags = [tuple(sorted({tag(a) for a in t['analysis']['analyses']})) for t in tokens]
        self.cache = {}

    def neighbors(self, i, radius, phrase=False):
        for direction in (-1, 1):
            for distance in range(1, radius + 1):
                j = i + direction * distance
                if not 0 <= j < len(self.tokens):
                    break
                raw = self.tokens[j]['raw']
                if raw in HARD or raw in {',', ':', '(', ')', '“', '”', '"'} or lower(raw) in COORD:
                    break
                yield j, direction, distance
                ts = self.tags[j]
                # Only unanimous barriers stop evidence; ambiguous readings remain
                # conditional possibilities. These are bounded windows, not gold clauses.
                if ts and all(t[4] in {'Fin', 'Conv', 'Part', 'Vnoun'} for t in ts):
                    break
                if phrase and (not ts or not any(t[2] in NOMINAL | {'DET'} and t[4] != 'Fin' for t in ts)):
                    break

    def features(self, tokens, i, a, family='combined'):
        if family not in (*FAMILIES, 'combined'):
            raise ValueError('UNKNOWN_FORMULA_FAMILY')
        self.reset(tokens)
        key = i, tag(a)
        if key not in self.cache:
            self.cache[key] = self._features(i, tag(a))
        fs = self.cache[key]
        return fs if family == 'combined' else {k: v for k, v in fs.items() if k.startswith(family + '.')}

    def _features(self, i, t):
        result = {}

        def collect(family, label, candidates):
            # Each tuple is a distinct nearby token's conditional support/conflict.
            if not candidates:
                return
            for state in ('support', 'conflict'):
                values = [x[state] for x in candidates]
                if max(values, default=0):
                    result[f'{family}.{label}.{state}.max'] = max(values)
                    result[f'{family}.{label}.{state}.sum'] = min(2., sum(values))
            if any(x['support'] and x['conflict'] for x in candidates):
                result[f'{family}.{label}.ambiguous'] = 1.

        def evidence(tags, score, distance):
            values = [score(other) for other in tags]
            scale = 1. / (1. + .2 * (distance - 1)) / max(1, len(values))
            return {'support': sum(x > 0 for x in values) * scale,
                    'conflict': sum(x < 0 for x in values) * scale}

        lemma, root, pos, case, vf, person, number, psor, npsor, voice = t
        if pos in NOMINAL and vf != 'Fin':
            left, right, numbers = [], [], []
            for j, direction, distance in self.neighbors(i, 6, phrase=True):
                if direction < 0:
                    def owner(other):
                        r = referent(other)
                        if other[3] != 'Gen' or not r:
                            return 0
                        if not psor:
                            return -1
                        return 1 if r[0] == psor else -1
                    left.append(evidence(self.tags[j], owner, distance))
                    if psor:
                        def owner_number(other):
                            r = referent(other)
                            if other[3] != 'Gen' or not r or r[0] != psor or not npsor:
                                return 0
                            # Third-person nominal plurality is not a required
                            # possessor-number agreement; pronouns are soft evidence.
                            if other[2] != 'PRON':
                                return 0
                            return 1 if r[1] == npsor else -1
                        numbers.append(evidence(self.tags[j], owner_number, distance))
                elif referent(t):
                    def possessed(other):
                        if other[2] not in NOMINAL or not other[7] or other[4] == 'Fin':
                            return 0
                        if case != 'Gen':
                            return -1
                        return 1 if referent(t)[0] == other[7] else -1
                    right.append(evidence(self.tags[j], possessed, distance))
            collect('poss', 'owner_left', left)
            collect('poss', 'owner_number', numbers)
            collect('poss', 'possessed_right', right)
            # The same owner evidence interacts with the target's actual case,
            # so possession-vs-accusative alternatives no longer collapse.
            collect('case', 'owner_left_' + case + ('_poss' if psor else '_no_poss'), left)
            collect('case', 'possessed_right_' + case, right)
            for direction, label in ((-1, 'left'), (1, 'right')):
                context = []
                for j, d, distance in self.neighbors(i, 8):
                    if d != direction:
                        continue
                    def predicate(other):
                        if other[1] != 'VERB' or other[2] != 'VERB' or other[4] != 'Fin' or case == 'Nom':
                            return 0
                        frames = self.frames.get(other[0] + '|' + other[9], {})
                        total = sum(frames.values())
                        if total < 3:
                            return 0
                        prob = (frames.get(case, 0) + .5) / (total + 3.)
                        return 1 if prob > 1 / 6 else -1
                    context.append(evidence(self.tags[j], predicate, distance))
                collect('case', 'predicate_' + label + '_' + case, context)

        # Predicate and subject sides are both scored, but a Gen pronoun is
        # never treated as an overt subject of the nearby finite predicate.
        if vf == 'Fin' and person:
            for direction, label in ((-1, 'left'), (1, 'right')):
                context = []
                for j, d, distance in self.neighbors(i, 8):
                    if d != direction:
                        continue
                    def subject(other):
                        if other[2] != 'PRON' or other[3] != 'Nom' or other[4] == 'Fin':
                            return 0
                        r = referent(other)
                        if not r:
                            return 0
                        match = r[0] == person and (person == '3' or r[1] == number)
                        return 1 if match else -1
                    context.append(evidence(self.tags[j], subject, distance))
                collect('person', 'subject_' + label, context)
        if pos == 'PRON' and case == 'Nom' and vf != 'Fin' and referent(t):
            r = referent(t)
            context = []
            for j, _, distance in self.neighbors(i, 8):
                def predicate_person(other):
                    if other[4] != 'Fin' or not other[5]:
                        return 0
                    return 1 if r[0] == other[5] and (r[0] == '3' or r[1] == other[6]) else -1
                context.append(evidence(self.tags[j], predicate_person, distance))
            collect('person', 'predicate_for_subject', context)
        return result
