# -*- coding: utf-8 -*-
"""
TurkTokenizer v5.3
==================
State/Lattice + Morphophonology + Transition Constraints çekirdeği.

Tasarım ilkeleri
----------------
1) Surface string ile underlying morphology ayrıdır.
2) Parser tek bir analize zorlamaz; geçerli adayları lattice olarak tutar.
3) Morfemlerin sırası "suffix listesi" değil, state -> transition -> state
   grafiği ile kısıtlanır.
4) Morfofonoloji, morfolojik kimlikten ayrı bir realization katmanıdır.
5) Disambiguation bu çekirdeğin dışında tutulur: önce aday uzayı, sonra ranking.
6) Bilinmeyen/nonce kökler grammar tarafından üretken biçimde işlenebilir.

Bu sürüm bir "çekirdek"tir. Türkçenin tüm morfem envanterinin akademik olarak
tamamlandığını iddia etmez; v5.2'den gelen isimlendirmeleri mümkün olduğunca
korur ve yeni mimariyi bunların üzerine kurar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import math
import re


# ---------------------------------------------------------------------------
# 1. MORPHOLOGICAL STATES
# ---------------------------------------------------------------------------

class MorphState(str, Enum):
    ROOT = "ROOT"
    DERIVED_NOMINAL = "DERIVED_NOMINAL"
    DERIVED_VERBAL = "DERIVED_VERBAL"
    FINITE_TAM = "FINITE_TAM"
    NONFINITE = "NONFINITE"
    NUMBERED = "NUMBERED"
    POSSESSED = "POSSESSED"
    CASED = "CASED"
    RELATIONAL = "RELATIONAL"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class Morph:
    """Underlying morpheme."""
    name: str
    feature: str
    category: str
    order_class: int
    surface_candidates: Tuple[str, ...] = ()
    weight: float = 1.0


@dataclass(frozen=True)
class Realization:
    """Surface realization of an underlying morph."""
    morph: str
    surface: str
    changes: Tuple[str, ...] = ()


@dataclass
class ParseNode:
    """One node in the morphological lattice."""
    state: MorphState
    position: int
    lemma: str
    surface: str
    features: Tuple[str, ...] = ()
    realizations: Tuple[Realization, ...] = ()
    score: float = 0.0
    notes: Tuple[str, ...] = ()

    def key(self) -> Tuple:
        return (
            self.state.value,
            self.position,
            self.lemma,
            self.features,
            self.surface,
        )


@dataclass
class ParseResult:
    lemma: str
    features: Tuple[str, ...]
    realizations: Tuple[Realization, ...]
    state: MorphState
    score: float
    complete: bool
    notes: Tuple[str, ...] = ()

    @property
    def chain(self) -> List[str]:
        return list(self.features)


# ---------------------------------------------------------------------------
# 2. MORPHOLOGY / MORPHOPHONOLOGY
# ---------------------------------------------------------------------------

VOWELS = "aeıioöuü"
FRONT_VOWELS = "eiöü"
BACK_VOWELS = "aıou"
ROUNDED_VOWELS = "öüou"
UNROUNDED_VOWELS = "eaiı"


def last_vowel(s: str) -> Optional[str]:
    for ch in reversed(s.lower()):
        if ch in VOWELS:
            return ch
    return None


def vowel_harmony_variants(stem: str, forms: Sequence[str]) -> Tuple[str, ...]:
    """
    Basit bir yüzey gerçekleştirme katmanı.
    forms, v5.2'de kullanılan yüzey şablonlarını içerebilir:
      A -> a/e
      I -> ı/i/u/ü
    """
    v = last_vowel(stem)
    if not v:
        return tuple(forms)

    out = []
    for form in forms:
        x = form
        if "A" in x:
            x = x.replace("A", "e" if v in FRONT_VOWELS else "a")
        if "I" in x:
            if v in "aı":
                x = x.replace("I", "ı")
            elif v in "ei":
                x = x.replace("I", "i")
            elif v == "o":
                x = x.replace("I", "u")
            elif v == "ö":
                x = x.replace("I", "ü")
            elif v == "u":
                x = x.replace("I", "u")
            elif v == "ü":
                x = x.replace("I", "ü")
        out.append(x)
    return tuple(dict.fromkeys(out))


def consonant_alternation(stem: str, following: str) -> Tuple[str, Tuple[str, ...]]:
    """
    Yaygın yüzey alternasyonları için konservatif bir çekirdek.
    Burada amaç bütün Türkçe sesbilgisini çözmek değil, underlying stem'i
    yüzey biçiminden ayırabilecek bir abstraction sağlamaktır.
    """
    if not stem:
        return stem, ()

    changes = []
    s = stem

    # p -> b, ç -> c, t -> d, k -> ğ/g gibi yumuşama adayları.
    if following and following[0] in "aeıioöuü":
        repl = {"p": "b", "ç": "c", "t": "d"}
        if s[-1] in repl:
            changes.append(f"{s[-1]}->{repl[s[-1]]}")
            s = s[:-1] + repl[s[-1]]
        elif s.endswith("k"):
            # kelimeye göre ğ/g ayrımı burada kesinleştirilmez.
            changes.append("k->ğ/g")
            s = s[:-1] + "ğ"
    return s, tuple(changes)


# ---------------------------------------------------------------------------
# 2. LEXICON + MORPHOPHONOLOGY
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AlternationClass:
    """
    Lexically conditioned stem alternation.

    `underlying_stem` may differ from the citation form.  This lets us model
    processes such as vowel deletion where the change is not just a
    final-segment substitution.
    """
    name: str
    underlying_final: str
    citation_final: Optional[str] = None
    before_vowel: Optional[str] = None
    before_consonant: Optional[str] = None
    surface_stem_before_vowel: Optional[str] = None
    surface_stem_before_consonant: Optional[str] = None
    lexical_pattern: Optional[str] = None


@dataclass(frozen=True)
class LexicalEntry:
    """
    Lexical representation independent of a particular surface word.

    origin is metadata only.  It MUST NOT itself trigger a phonological rule.
    `alternation_class` carries the actual productive behavior.
    """
    lemma: str
    lexical_stem: str
    category: str = "UNKNOWN"
    origin: Optional[str] = None
    alternation_class: Optional[str] = None
    tags: Tuple[str, ...] = ()


@dataclass(frozen=True)
class MorphologicalEnvironment:
    """Environment seen by a morphophonological rule."""
    suffix_initial: str
    suffix_surface: str
    boundary: str = "+"
    position: str = "STEM_FINAL"


@dataclass(frozen=True)
class RuleTrace:
    rule: str
    direction: str
    before: str
    after: str
    environment: str
    note: str = ""


@dataclass(frozen=True)
class InverseCandidate:
    """One lexical candidate reconstructed from a surface stem."""
    lemma: str
    lexical_stem: str
    surface_stem: str
    alternation_class: Optional[str]
    traces: Tuple[RuleTrace, ...] = ()
    cost: float = 0.0


class AlternationRegistry:
    """
    Registry of explicit lexical alternation classes.

    This is intentionally small and conservative.  It does not assert that
    every Turkish word belongs to a single universal alternation class.
    """

    def __init__(self):
        self.classes: Dict[str, AlternationClass] = {}

    def add(self, cls: AlternationClass):
        self.classes[cls.name] = cls

    def get(self, name: Optional[str]) -> Optional[AlternationClass]:
        return self.classes.get(name) if name else None


class Lexicon:
    """
    Lexical layer.  The dictionary is an aid to candidate generation, not a
    prerequisite for productive morphology.
    """

    def __init__(self):
        self.entries: Dict[str, LexicalEntry] = {}
        self.alternations = AlternationRegistry()
        self._build_default_alternations()
        self._build_default_entries()

    def _build_default_alternations(self):
        # Final stop alternation:
        # p -> b, ç -> c, t -> d, k -> ğ/g in vowel-initial environments.
        self.alternations.add(AlternationClass(
            "FINAL_STOP_VOICING_P", "p", "p", "b", "p"
        ))
        self.alternations.add(AlternationClass(
            "FINAL_STOP_VOICING_C", "ç", "ç", "c", "ç"
        ))
        self.alternations.add(AlternationClass(
            "FINAL_STOP_VOICING_T", "t", "t", "d", "t"
        ))
        self.alternations.add(AlternationClass(
            "FINAL_STOP_VOICING_K", "k", "k", "ğ", "k"
        ))

        # Lexically conditioned k -> g/ğ distinction.  The important design
        # point is that we do NOT collapse these into one universal rule.
        self.alternations.add(AlternationClass(
            "FINAL_K_TO_G", "k", "k", "g", "k"
        ))

        # Consonant-cluster alternation, e.g. renk + i -> rengi.
        self.alternations.add(AlternationClass(
            "NK_TO_NG", "nk", "nk", "ng", "nk"
        ))

        # Stem-internal vowel deletion classes.  These are represented as
        # whole-stem alternants, not as a generic "delete any vowel" rule.
        self.alternations.add(AlternationClass(
            "VOWEL_DROP_AĞIZ", "z", "z", "z", "z",
            lexical_pattern="^ağız$"
        ))
        self.alternations.add(AlternationClass(
            "VOWEL_DROP_BURUN", "n", "n", "n", "n",
            lexical_pattern="^burun$"
        ))
        self.alternations.add(AlternationClass(
            "VOWEL_DROP_OMUZ", "z", "z", "z", "z",
            lexical_pattern="^omuz$"
        ))
        self.alternations.add(AlternationClass(
            "VOWEL_DROP_AĞIZ_LIKE", "r", "r", "r", "r",
            lexical_pattern="^karın$"
        ))

    def _build_default_entries(self):
        # The list is deliberately explicit: alternation behavior is lexical
        # data, while origin is metadata and is never used as a rule trigger.
        entries = [
            LexicalEntry("kitap", "kitap", "NOUN", "ARABIC",
                         "FINAL_STOP_VOICING_P"),
            LexicalEntry("ağaç", "ağaç", "NOUN", "TURKIC",
                         "FINAL_STOP_VOICING_C"),
            LexicalEntry("renk", "renk", "NOUN", "PERSIAN",
                         "NK_TO_NG"),
            LexicalEntry("yurt", "yurt", "NOUN", "TURKIC",
                         "FINAL_STOP_VOICING_T"),
            LexicalEntry("ev", "ev", "NOUN", "TURKIC", None),
            LexicalEntry("çocuk", "çocuk", "NOUN", "TURKIC", None),
            LexicalEntry("ağız", "ağız", "NOUN", "TURKIC",
                         "VOWEL_DROP_AĞIZ"),
            LexicalEntry("burun", "burun", "NOUN", "TURKIC",
                         "VOWEL_DROP_BURUN"),
            LexicalEntry("omuz", "omuz", "NOUN", "TURKIC",
                         "VOWEL_DROP_OMUZ"),
            LexicalEntry("karın", "karın", "NOUN", "TURKIC",
                         "VOWEL_DROP_AĞIZ_LIKE"),
        ]
        for e in entries:
            self.entries[e.lemma] = e

    def add(self, entry: LexicalEntry):
        self.entries[entry.lemma] = entry

    def get(self, lemma: str) -> Optional[LexicalEntry]:
        return self.entries.get(lemma)

    def candidates_by_surface_stem(self, surface_stem: str) -> List[LexicalEntry]:
        out = []
        for e in self.entries.values():
            if e.lexical_stem == surface_stem or e.lemma == surface_stem:
                out.append(e)
        return out


# ---------------------------------------------------------------------------
# 2A. ORDERED MORPHOPHONOLOGICAL RULES
# ---------------------------------------------------------------------------

class MorphophonologicalRule:
    """
    Base rule.

    Rules are deliberately explicit and ordered.  The engine can use the
    same rule objects in forward and inverse directions.
    """
    name = "RULE"

    def forward(self, stem: str, env: MorphologicalEnvironment):
        return stem, None

    def inverse(self, stem: str, env: MorphologicalEnvironment):
        return stem, None


class FinalStopVoicingRule(MorphophonologicalRule):
    """
    p→b, ç→c, t→d, k→ğ before vowel-initial suffixes.

    This is a conservative abstraction.  It does not claim that every k-final
    lexical item universally maps to ğ; lexical exceptions can be represented
    by another AlternationClass or an explicit lexical entry.
    """
    name = "FINAL_STOP_VOICING"

    MAP = {"p": "b", "ç": "c", "t": "d", "k": "ğ"}

    def forward(self, stem: str, env: MorphologicalEnvironment):
        if not stem or not env.suffix_initial or env.suffix_initial not in VOWELS:
            return stem, None
        if stem[-1] in self.MAP:
            new = stem[:-1] + self.MAP[stem[-1]]
            return new, RuleTrace(
                self.name, "forward", stem, new,
                "VOWEL_INITIAL_SUFFIX",
                "final stop alternation"
            )
        return stem, None

    def inverse(self, stem: str, env: MorphologicalEnvironment):
        if not stem or not env.suffix_initial or env.suffix_initial not in VOWELS:
            return stem, None
        inv = {v: k for k, v in self.MAP.items()}
        if stem[-1] in inv:
            new = stem[:-1] + inv[stem[-1]]
            return new, RuleTrace(
                self.name, "inverse", stem, new,
                "VOWEL_INITIAL_SUFFIX",
                "surface→lexical stem reconstruction"
            )
        return stem, None



class WholeStemAlternationRule(MorphophonologicalRule):
    """Explicit lexical stem alternant for non-local changes such as vowel drop."""

    def __init__(self, entry: LexicalEntry, cls: AlternationClass):
        self.entry = entry
        self.cls = cls
        self.name = f"LEXICAL_{cls.name}"

    def _surface(self) -> Optional[str]:
        if not self.cls.lexical_pattern:
            return None
        if re.match(self.cls.lexical_pattern, self.entry.lexical_stem):
            # Explicit dictionary alternants.  Keep this table deliberately
            # conservative instead of inferring arbitrary vowel deletion.
            table = {
                "ağız": "ağz",
                "burun": "burn",
                "omuz": "omz",
                "karın": "karn",
            }
            return table.get(self.entry.lexical_stem)
        return None

    def forward(self, stem: str, env: MorphologicalEnvironment):
        if env.suffix_initial not in VOWELS:
            return stem, None
        surface = self._surface()
        if surface and stem == self.entry.lexical_stem:
            return surface, RuleTrace(
                self.name, "forward", stem, surface,
                "VOWEL_INITIAL_SUFFIX",
                "lexical stem-internal vowel deletion"
            )
        return stem, None

    def inverse(self, stem: str, env: MorphologicalEnvironment):
        if env.suffix_initial not in VOWELS:
            return stem, None
        surface = self._surface()
        if surface and stem == surface:
            return self.entry.lexical_stem, RuleTrace(
                self.name, "inverse", stem, self.entry.lexical_stem,
                "VOWEL_INITIAL_SUFFIX",
                "surface→lexical stem reconstruction"
            )
        return stem, None


class AlternationRule(MorphophonologicalRule):
    """
    Lexicon-driven rule.  Unlike FinalStopVoicingRule, this rule only fires
    for an explicit LexicalEntry/AlternationClass.
    """
    def __init__(self, cls: AlternationClass):
        self.cls = cls
        self.name = f"LEXICAL_{cls.name}"

    def forward(self, stem: str, env: MorphologicalEnvironment):
        if not stem.endswith(self.cls.underlying_final):
            return stem, None
        target = (
            self.cls.before_vowel
            if env.suffix_initial in VOWELS
            else self.cls.before_consonant
        )
        if target and target != self.cls.underlying_final:
            new = stem[:-len(self.cls.underlying_final)] + target
            return new, RuleTrace(
                self.name, "forward", stem, new,
                "VOWEL_INITIAL_SUFFIX" if env.suffix_initial in VOWELS
                else "CONSONANT_INITIAL_SUFFIX",
                "lexicon-conditioned alternation"
            )
        return stem, None

    def inverse(self, stem: str, env: MorphologicalEnvironment):
        target = (
            self.cls.before_vowel
            if env.suffix_initial in VOWELS
            else self.cls.before_consonant
        )
        if target and stem.endswith(target):
            new = stem[:-1] + self.cls.underlying_final
            return new, RuleTrace(
                self.name, "inverse", stem, new,
                "VOWEL_INITIAL_SUFFIX" if env.suffix_initial in VOWELS
                else "CONSONANT_INITIAL_SUFFIX",
                "surface→lexical stem reconstruction"
            )
        return stem, None


class OrderedMorphophonology:
    """
    Forward + inverse engine.

    Important:
      - forward: lexical stem -> surface stem
      - inverse: surface stem -> lexical stem candidates
    """

    def __init__(self, lexicon: Optional[Lexicon] = None):
        self.lexicon = lexicon or Lexicon()
        self.rules: List[MorphophonologicalRule] = [
            FinalStopVoicingRule(),
        ]

    def _suffix_initial(self, suffix_surface: str) -> str:
        for ch in suffix_surface:
            if ch.isalpha():
                return ch.lower()
        return ""

    def forward(self, entry: LexicalEntry, suffix_surface: str) -> Tuple[str, Tuple[RuleTrace, ...]]:
        env = MorphologicalEnvironment(
            suffix_initial=self._suffix_initial(suffix_surface),
            suffix_surface=suffix_surface,
        )
        stem = entry.lexical_stem
        traces = []

        if entry.alternation_class:
            cls = self.lexicon.alternations.get(entry.alternation_class)
            if cls:
                if cls.lexical_pattern:
                    stem, trace = WholeStemAlternationRule(entry, cls).forward(stem, env)
                else:
                    stem, trace = AlternationRule(cls).forward(stem, env)
                if trace:
                    traces.append(trace)

        for rule in self.rules:
            stem, trace = rule.forward(stem, env)
            if trace:
                traces.append(trace)

        return stem, tuple(traces)

    def inverse(
        self,
        surface_stem: str,
        suffix_surface: str,
    ) -> List[InverseCandidate]:
        env = MorphologicalEnvironment(
            suffix_initial=self._suffix_initial(suffix_surface),
            suffix_surface=suffix_surface,
        )

        candidates = []

        # 1) Lexicon-conditioned inverse candidates.
        for entry in self.lexicon.entries.values():
            if entry.alternation_class:
                cls = self.lexicon.alternations.get(entry.alternation_class)
                if not cls:
                    continue

                if cls.lexical_pattern:
                    lexical, trace = WholeStemAlternationRule(entry, cls).inverse(
                        surface_stem, env
                    )
                    if trace and lexical == entry.lexical_stem:
                        candidates.append(InverseCandidate(
                            entry.lemma, lexical, surface_stem,
                            entry.alternation_class, (trace,), 0.05
                        ))
                    continue

                target = (
                    cls.before_vowel
                    if env.suffix_initial in VOWELS
                    else cls.before_consonant
                )
                underlying = cls.underlying_final
                if target and target != underlying and surface_stem.endswith(target):
                    lexical = surface_stem[:-len(target)] + underlying
                    if lexical == entry.lexical_stem:
                        candidates.append(InverseCandidate(
                            entry.lemma, lexical, surface_stem,
                            entry.alternation_class, (), 0.1
                        ))

        # 2) Generic inverse candidates.  Kept with a higher cost so lexical
        # evidence wins when available, but productive morphology remains.
        for rule in reversed(self.rules):
            lexical, trace = rule.inverse(surface_stem, env)
            if trace and lexical != surface_stem:
                candidates.append(InverseCandidate(
                    lexical, lexical, surface_stem, None,
                    (trace,), 0.7
                ))

        # 3) No-alternation candidate always survives.
        candidates.append(InverseCandidate(
            surface_stem, surface_stem, surface_stem, None, (), 1.0
        ))

        # Deduplicate by lemma/stem/class.
        uniq = {}
        for c in candidates:
            uniq[(c.lemma, c.lexical_stem, c.alternation_class)] = c
        return sorted(uniq.values(), key=lambda c: c.cost)


# Compatibility façade used by v5.3 parser code.
class Morphophonology:
    """
    Backward-compatible façade.

    v5.3 parser still asks for surface suffix variants; v5.3.1 adds the
    lexical/ordered layer without forcing the parser rewrite in one step.
    """

    TEMPLATES: Dict[str, Tuple[str, ...]] = {
        "PLURAL": ("lAr",),
        "POSS_1SG": ("(I)m",),
        "POSS_2SG": ("(I)n",),
        "POSS_3SG": ("(s)I",),
        "POSS_1PL": ("(I)mIz",),
        "POSS_2PL": ("(I)nIz",),
        "POSS_3PL": ("lArI",),
        "DATIVE": ("(y)A",),
        "LOCATIVE": ("dA",),
        "ABLATIVE": ("dAn",),
        "GENITIVE": ("(n)In",),
        "ACCUSATIVE": ("(y)I",),
        "COMITATIVE": ("(y)lA",),
        "RELATIVE_KI": ("ki",),
        "PAST": ("dI",),
        "EVIDENTIAL": ("mIş",),
        "FUTURE": ("(y)AcAk",),
        "PROGRESSIVE": ("Iyor",),
        "NEGATION": ("mA",),
        "ABILITY": ("(y)AbIl",),
        "NEGATIVE_ABILITY": ("(y)AmA",),
        "PARTICIPLE_PRESENT": ("(y)An",),
        "PARTICIPLE_PAST": ("dIk",),
        "PARTICIPLE_FUTURE": ("(y)AcAk",),
        "NOMINALIZER_LIK": ("lIk",),
        "NOMINALIZER_MA": ("mA",),
        "DERIVATIONAL_LA": ("lA",),
        "DERIVATIONAL_LI": ("lI",),
        "DERIVATIONAL_LU": ("lU",),
        "DERIVATIONAL_SIZ": ("sIz",),
        "DERIVATIONAL_CIL": ("cIl",),
        "INCHOATIVE_LAS": ("lAş",),
        "CAUSATIVE": ("tIr",),
        "PASSIVE": ("Il",),
    }

    def __init__(self):
        self.lexicon = Lexicon()
        self.ordered = OrderedMorphophonology(self.lexicon)

    def realize(self, stem: str, morph: str) -> List[Realization]:
        templates = self.TEMPLATES.get(morph, ())
        if not templates:
            return [Realization(morph, "", ("NO_TEMPLATE",))]

        variants = vowel_harmony_variants(stem, templates)
        results = []
        for form in variants:
            surface = form
            if surface.startswith("(y)"):
                surface = surface[3:]
                if stem and stem[-1] in VOWELS:
                    surface = "y" + surface
            if surface.startswith("(n)"):
                surface = surface[3:]
                if stem and stem[-1] in VOWELS:
                    surface = "n" + surface
            if surface.startswith("(s)"):
                surface = surface[3:]
                if stem and stem[-1] in VOWELS:
                    surface = "s" + surface
            if surface.startswith("(I)"):
                surface = surface[3:]
            results.append(Realization(morph, surface))
        return results

    def surface_variants(self, stem: str, morph: str) -> Tuple[str, ...]:
        return tuple(r.surface for r in self.realize(stem, morph))


# ---------------------------------------------------------------------------
# 2B. INVERSE SURFACE STEM RECONSTRUCTION
# ---------------------------------------------------------------------------

class InverseMorphophonology:
    """
    Surface word -> suffix candidate + lexical stem candidates.

    This is deliberately independent from transition constraints.  It answers:
      "Bu yüzey parçası hangi lexical stemlerden gelmiş olabilir?"

    Grammar later answers:
      "Bu lexical analysis bu state'te izinli mi?"
    """

    def __init__(self, lexicon: Optional[Lexicon] = None):
        self.lexicon = lexicon or Lexicon()
        self.engine = OrderedMorphophonology(self.lexicon)

    def recover(
        self,
        surface_stem: str,
        suffix_surface: str,
    ) -> List[InverseCandidate]:
        return self.engine.inverse(surface_stem, suffix_surface)


# ---------------------------------------------------------------------------
# 3. TRANSITION CONSTRAINTS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Transition:
    src: MorphState
    feature: str
    dst: MorphState
    cost: float = 1.0
    note: str = ""


class TransitionGrammar:
    """
    Türkçenin morfotaktik çekirdeği.

    Buradaki amaç "her suffix her yerde olabilir" modelini kırmaktır.
    Aynı feature farklı state'lerden farklı sonuçlara gidebilir.
    """

    def __init__(self):
        self.transitions: Dict[MorphState, List[Transition]] = {}
        self._build()

    def add(self, src: MorphState, feature: str, dst: MorphState,
            cost: float = 1.0, note: str = ""):
        self.transitions.setdefault(src, []).append(
            Transition(src, feature, dst, cost, note)
        )

    def _build(self):
        # Nominal derivation
        for f in (
            "NOMINALIZER_LIK", "NOMINALIZER_MA",
            "DERIVATIONAL_LI", "DERIVATIONAL_LU",
            "DERIVATIONAL_SIZ", "DERIVATIONAL_CIL",
        ):
            self.add(MorphState.ROOT, f, MorphState.DERIVED_NOMINAL)

        # Verbal derivation
        for f in (
            "DERIVATIONAL_LA", "INCHOATIVE_LAS",
            "CAUSATIVE", "PASSIVE",
        ):
            self.add(MorphState.ROOT, f, MorphState.DERIVED_VERBAL)
            self.add(MorphState.DERIVED_VERBAL, f, MorphState.DERIVED_VERBAL)

        # Derivational chaining.
        for f in ("CAUSATIVE", "PASSIVE"):
            self.add(MorphState.DERIVED_VERBAL, f, MorphState.DERIVED_VERBAL)

        for f in (
            "PAST", "EVIDENTIAL", "FUTURE", "PROGRESSIVE",
            "NEGATION", "ABILITY", "NEGATIVE_ABILITY",
        ):
            self.add(MorphState.ROOT, f, MorphState.FINITE_TAM)
            self.add(MorphState.DERIVED_VERBAL, f, MorphState.FINITE_TAM)
            self.add(MorphState.FINITE_TAM, f, MorphState.FINITE_TAM)

        # Nonfinite paths.
        for f in (
            "PARTICIPLE_PRESENT", "PARTICIPLE_PAST", "PARTICIPLE_FUTURE",
        ):
            self.add(MorphState.ROOT, f, MorphState.NONFINITE)
            self.add(MorphState.DERIVED_VERBAL, f, MorphState.NONFINITE)
            self.add(MorphState.NONFINITE, f, MorphState.NONFINITE)

        # Number / possession / case.
        for src in (
            MorphState.ROOT, MorphState.DERIVED_NOMINAL,
            MorphState.NONFINITE, MorphState.RELATIONAL,
        ):
            self.add(src, "PLURAL", MorphState.NUMBERED)

        for src in (
            MorphState.ROOT, MorphState.DERIVED_NOMINAL,
            MorphState.NONFINITE, MorphState.NUMBERED,
        ):
            self.add(src, "POSS_1SG", MorphState.POSSESSED)
            self.add(src, "POSS_2SG", MorphState.POSSESSED)
            self.add(src, "POSS_3SG", MorphState.POSSESSED)
            self.add(src, "POSS_1PL", MorphState.POSSESSED)
            self.add(src, "POSS_2PL", MorphState.POSSESSED)
            self.add(src, "POSS_3PL", MorphState.POSSESSED)

        # Case can follow nominal/possessed/nonfinite/numbered.
        for src in (
            MorphState.ROOT, MorphState.DERIVED_NOMINAL,
            MorphState.NONFINITE, MorphState.NUMBERED,
            MorphState.POSSESSED, MorphState.RELATIONAL,
        ):
            for f in ("DATIVE", "LOCATIVE", "ABLATIVE", "GENITIVE",
                      "ACCUSATIVE", "COMITATIVE"):
                self.add(src, f, MorphState.CASED)

        # -ki as a relational layer after locative/possessive+locative.
        self.add(MorphState.CASED, "RELATIVE_KI", MorphState.RELATIONAL)
        self.add(MorphState.RELATIONAL, "PLURAL", MorphState.NUMBERED)

        # Person features. 3SG is explicitly represented as ZERO.
        for src in (MorphState.FINITE_TAM, MorphState.DERIVED_VERBAL):
            for p in ("PERSON_1SG", "PERSON_2SG", "PERSON_3SG",
                      "PERSON_1PL", "PERSON_2PL", "PERSON_3PL"):
                self.add(src, p, MorphState.COMPLETE, cost=0.0,
                         note="finite agreement")
        self.add(MorphState.NONFINITE, "PERSON_1SG", MorphState.COMPLETE, cost=0.0)
        self.add(MorphState.NONFINITE, "PERSON_2SG", MorphState.COMPLETE, cost=0.0)
        self.add(MorphState.NONFINITE, "PERSON_3SG", MorphState.COMPLETE, cost=0.0)
        self.add(MorphState.NONFINITE, "PERSON_1PL", MorphState.COMPLETE, cost=0.0)
        self.add(MorphState.NONFINITE, "PERSON_2PL", MorphState.COMPLETE, cost=0.0)
        self.add(MorphState.NONFINITE, "PERSON_3PL", MorphState.COMPLETE, cost=0.0)

        # Nominal complete states.
        for src in (
            MorphState.ROOT, MorphState.DERIVED_NOMINAL,
            MorphState.NUMBERED, MorphState.POSSESSED,
            MorphState.CASED, MorphState.RELATIONAL,
        ):
            self.add(src, "COMPLETE", MorphState.COMPLETE, cost=0.0)

    def allowed(self, state: MorphState, feature: str) -> List[Transition]:
        return [
            t for t in self.transitions.get(state, ())
            if t.feature == feature
        ]

    def can_transition(self, state: MorphState, feature: str) -> bool:
        return bool(self.allowed(state, feature))

    def next_state(self, state: MorphState, feature: str) -> Optional[MorphState]:
        ts = self.allowed(state, feature)
        return ts[0].dst if ts else None


# ---------------------------------------------------------------------------
# 4. MORPHOLOGICAL LATTICE
# ---------------------------------------------------------------------------

class MorphologicalLattice:
    def __init__(self):
        self.nodes: List[ParseNode] = []

    def add(self, node: ParseNode):
        self.nodes.append(node)

    def sorted_nodes(self) -> List[ParseNode]:
        return sorted(self.nodes, key=lambda n: (n.position, n.score))

    def finals(self) -> List[ParseNode]:
        return [
            n for n in self.nodes
            if n.state == MorphState.COMPLETE
        ]


# ---------------------------------------------------------------------------
# 5. CORE PARSER
# ---------------------------------------------------------------------------

class TurkishMorphologyV53:
    """
    Çekirdek parser.

    Not:
      - Bu sınıf deliberate olarak "closed-world" bir sözlük zorlamaz.
      - Root detection için verilen lemma sözlüğü kullanılabilir.
      - Bilinmeyen root, geçerli morfotaktik devam varsa aday olarak tutulur.
    """

    FEATURE_ORDER = [
        "PLURAL",
        "POSS_1SG", "POSS_2SG", "POSS_3SG", "POSS_1PL", "POSS_2PL", "POSS_3PL",
        "DATIVE", "LOCATIVE", "ABLATIVE", "GENITIVE", "ACCUSATIVE", "COMITATIVE",
        "RELATIVE_KI",
        "NEGATION", "ABILITY", "NEGATIVE_ABILITY",
        "PARTICIPLE_PRESENT", "PARTICIPLE_PAST", "PARTICIPLE_FUTURE",
        "PAST", "EVIDENTIAL", "FUTURE", "PROGRESSIVE",
        "DERIVATIONAL_LI", "DERIVATIONAL_LU", "DERIVATIONAL_SIZ", "DERIVATIONAL_CIL",
        "NOMINALIZER_LIK", "NOMINALIZER_MA",
        "DERIVATIONAL_LA", "INCHOATIVE_LAS", "CAUSATIVE", "PASSIVE",
        "PERSON_1SG", "PERSON_2SG", "PERSON_3SG", "PERSON_1PL", "PERSON_2PL", "PERSON_3PL",
    ]

    # Çok kaba stem adayları; v5.3'te amaç root-space üretmek.
    COMMON_ROOTS = {
        "ev","kitap","çocuk","araba","baş","güzel","sorumlu","başarısız",
        "genç","köy","tuz","yağ","akıl","renk","ağaç","ağız","burun",
        "oğul","karın","şehir","fikir","gel","git","yap","yaz","oku","anla",
        "çalış","temiz","hız","başla","karşılaştır","türkçe","zengin","dar",
        "geniş","görüş","evsiz","başarısız","sorumluluk","güzellik",
    }

    def __init__(self, roots: Optional[Iterable[str]] = None,
                 lexicon: Optional[Lexicon] = None):
        self.grammar = TransitionGrammar()
        self.phono = Morphophonology()
        self.lexicon = lexicon or self.phono.lexicon
        self.inverse_phono = InverseMorphophonology(self.lexicon)
        self.roots = set(roots or self.COMMON_ROOTS)
        self.roots.update(self.lexicon.entries.keys())

    def lexical_candidates(self, surface_stem: str, suffix_surface: str = "") -> List[InverseCandidate]:
        return self.inverse_phono.recover(surface_stem, suffix_surface)

    def root_candidates(self, word: str) -> List[str]:
        """
        En uzun bilinen kökleri önce dener.
        Bilinmeyen kelimede conservative fallback:
        word'un kendisi root adayıdır; böylece nonce productivity tamamen
        dictionary'ye kilitlenmez.
        """
        roots = [r for r in self.roots if word.startswith(r)]
        if roots:
            return sorted(roots, key=len, reverse=True)
        return [word]

    def _suffix_candidates(self, remaining: str, stem: str) -> List[Tuple[str, str]]:
        """
        Yüzeyden feature adayları üretir. Bu aşama yalnızca candidate generator'dır;
        transition grammar son sözü söyler.
        """
        candidates = []
        for feature in self.FEATURE_ORDER:
            for surface in self.phono.surface_variants(stem, feature):
                if surface and remaining.startswith(surface):
                    candidates.append((feature, surface))
        # Uzun yüzey biçimleri önce.
        candidates.sort(key=lambda x: len(x[1]), reverse=True)
        return candidates

    def parse(self, word: str, max_nodes: int = 500) -> MorphologicalLattice:
        lattice = MorphologicalLattice()
        frontier: List[ParseNode] = []

        for root in self.root_candidates(word):
            if not word.startswith(root):
                continue
            frontier.append(ParseNode(
                state=MorphState.ROOT,
                position=len(root),
                lemma=root,
                surface=word,
                score=0.0,
                notes=("root_candidate",),
            ))

        seen = set()
        steps = 0

        while frontier and steps < max_nodes:
            steps += 1
            node = frontier.pop(0)
            key = node.key()
            if key in seen:
                continue
            seen.add(key)
            lattice.add(node)

            if node.position >= len(word):
                # Nominal analizler için implicit COMPLETE adayı.
                if node.state != MorphState.COMPLETE:
                    final = ParseNode(
                        state=MorphState.COMPLETE,
                        position=node.position,
                        lemma=node.lemma,
                        surface=word,
                        features=node.features,
                        realizations=node.realizations,
                        score=node.score,
                        notes=node.notes + ("implicit_complete",),
                    )
                    lattice.add(final)
                continue

            remaining = word[node.position:]
            # Underlying stem = prefix consumed so far. Candidate surface matching
            # conservatively uses the original lemma plus reconstructed prefix.
            consumed = word[:node.position]
            stem_for_phono = consumed

            for feature, surf in self._suffix_candidates(
                remaining, stem_for_phono
            ):
                transitions = self.grammar.allowed(node.state, feature)
                if not transitions:
                    continue

                for tr in transitions:
                    new_pos = node.position + len(surf)
                    if new_pos > len(word):
                        continue

                    realization = Realization(feature, surf)
                    child = ParseNode(
                        state=tr.dst,
                        position=new_pos,
                        lemma=node.lemma,
                        surface=word,
                        features=node.features + (feature,),
                        realizations=node.realizations + (realization,),
                        score=node.score + tr.cost + len(surf) * 0.001,
                        notes=node.notes + ((tr.note,) if tr.note else ()),
                    )
                    frontier.append(child)

        return lattice

    def analyze(self, word: str, n_best: int = 20) -> List[ParseResult]:
        lattice = self.parse(word)
        candidates = []
        seen = set()

        for n in lattice.finals():
            key = (n.lemma, n.features)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(ParseResult(
                lemma=n.lemma,
                features=n.features,
                realizations=n.realizations,
                state=n.state,
                score=n.score,
                complete=True,
                notes=n.notes,
            ))

        candidates.sort(key=lambda x: x.score)
        return candidates[:n_best]


# ---------------------------------------------------------------------------
# 6. DISAMBIGUATOR
# ---------------------------------------------------------------------------

class TurkishMorphDisambiguatorV53:
    """
    Ranking katmanı.

    v5.3 çekirdeğinde ranking grammar'dan ayrıdır.
    İlk sürümde yalnızca yapısal skor kullanılır.
    İleride corpus/context/semantic ranking buraya eklenebilir.
    """

    def __init__(self, parser: Optional[TurkishMorphologyV53] = None):
        self.parser = parser or TurkishMorphologyV53()

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        results = self.parser.analyze(word, n_best=n_best)
        # Daha kısa ve grammar'a uygun analizleri öncele.
        return sorted(
            results,
            key=lambda r: (
                r.score,
                len(r.features),
                r.lemma != word,
            )
        )[:n_best]


# ---------------------------------------------------------------------------
# 7. BENCHMARK HELPERS
# ---------------------------------------------------------------------------

def chain_of(result: ParseResult) -> List[str]:
    return result.chain


def evaluate_case(
    analyzer: TurkishMorphDisambiguatorV53,
    word: str,
    gold_lemma: str,
    gold_chain: Sequence[str],
    n_best: int = 20,
) -> dict:
    analyses = analyzer.analyze_word(word, n_best=n_best)
    best = analyses[0] if analyses else None

    exact = bool(
        best
        and best.lemma == gold_lemma
        and list(best.features) == list(gold_chain)
    )

    return {
        "word": word,
        "gold_lemma": gold_lemma,
        "gold_chain": list(gold_chain),
        "actual_lemma": best.lemma if best else None,
        "actual_chain": list(best.features) if best else [],
        "exact": exact,
        "coverage": bool(analyses),
        "n_best": len(analyses),
    }



def morphophonology_test() -> dict:
    """
    v5.3.2 focused inverse/forward regression suite.

    This is NOT a substitute for the project's 260-item Benchmark v2:
    that benchmark file was not available in the accessible file set in this
    turn, so the exact 260-item score is intentionally not fabricated.
    """
    lex = Lexicon()
    engine = OrderedMorphophonology(lex)

    cases = {
        "kitabı": ("kitab", "ı", "kitap"),
        "kitapsız": ("kitap", "sız", "kitap"),
        "kitaptan": ("kitap", "tan", "kitap"),
        "ağacı": ("ağac", "ı", "ağaç"),
        "rengi": ("reng", "i", "renk"),
        "ağızı": ("ağız", "ı", "ağız"),   # negative control: actual form is ağızı only if lexical process is not applied
        "ağzı": ("ağz", "ı", "ağız"),
        "burnu": ("burn", "u", "burun"),
        "omzu": ("omz", "u", "omuz"),
        "karnı": ("karn", "ı", "karın"),
    }

    report = {}
    for word, (surface_stem, suffix, expected) in cases.items():
        inv = engine.inverse(surface_stem, suffix)
        report[word] = {
            "expected": expected,
            "expected_found": any(x.lemma == expected for x in inv),
            "top": inv[0].lemma if inv else None,
            "candidates": [
                {
                    "lemma": x.lemma,
                    "lexical_stem": x.lexical_stem,
                    "cost": x.cost,
                    "traces": [
                        {
                            "rule": t.rule,
                            "direction": t.direction,
                            "before": t.before,
                            "after": t.after,
                            "environment": t.environment,
                        } for t in x.traces
                    ],
                } for x in inv[:5]
            ],
        }

    # Forward realization checks.
    forward_cases = [
        ("kitap", "ı", "kitab"),
        ("kitap", "sız", "kitap"),
        ("renk", "i", "reng"),
        ("ağaç", "ı", "ağac"),
        ("ağız", "ı", "ağz"),
        ("burun", "u", "burn"),
        ("omuz", "u", "omz"),
        ("karın", "ı", "karn"),
    ]
    forward = {}
    for lemma, suffix, expected_stem in forward_cases:
        entry = lex.get(lemma)
        stem, traces = engine.forward(entry, suffix)
        forward[f"{lemma}+{suffix}"] = {
            "expected_stem": expected_stem,
            "actual_stem": stem,
            "pass": stem == expected_stem,
            "traces": [t.rule for t in traces],
        }

    report["_forward"] = forward
    return report


def run_benchmark_v2_260(benchmark_words: Optional[List[str]] = None) -> dict:
    """
    Run the exact supplied Benchmark v2 list when available.

    Expected input: the same 260 surface words used by the project.
    The function deliberately refuses to manufacture missing benchmark items.
    """
    if benchmark_words is None:
        return {
            "status": "NOT_RUN",
            "reason": "Benchmark v2 260-item dataset is not available in this turn."
        }

    if len(benchmark_words) != 260:
        raise ValueError(f"Expected exactly 260 benchmark items, got {len(benchmark_words)}")

    parser = TurkishMorphTokenizer()
    rows = []
    for word in benchmark_words:
        rows.append({
            "word": word,
            "analysis": parser.analyze(word) if hasattr(parser, "analyze") else None
        })
    return {"status": "RUN", "n": 260, "rows": rows}


def smoke_test() -> dict:
    """
    Kodun temel state/lattice davranışını doğrular.
    Bu test tam linguistik benchmark değildir.
    """
    parser = TurkishMorphDisambiguatorV53()

    probes = [
        "evler",
        "evde",
        "evden",
        "evimizden",
        "kitabı",
        "kitabın",
        "geldi",
        "gelmedi",
        "gelecek",
        "gelen",
        "evdeki",
    ]

    report = {}
    for word in probes:
        analyses = parser.analyze_word(word, n_best=5)
        report[word] = [
            {
                "lemma": a.lemma,
                "chain": a.chain,
                "score": a.score,
            }
            for a in analyses
        ]

    return report


if __name__ == "__main__":
    print("TurkTokenizer v5.3.2 — Lexical Alternations + Vowel Drop + Inverse Morphophonology")
    print("=" * 88)
    print("\nMORPHOPHONOLOGY REGRESSION")
    for word, result in morphophonology_test().items():
        print(f"\n{word}: expected_found={result['expected_found']}")
        for c in result["candidates"][:4]:
            print(f"  {c['lemma']} / {c['lexical_stem']} [cost={c['cost']}]")
            for t in c["traces"]:
                print(f"    {t['rule']}: {t['before']} -> {t['after']} ({t['direction']})")
    print("\nSTATE/LATTICE SMOKE TEST")
    print("=" * 72)
    report = smoke_test()
    for word, analyses in report.items():
        print(f"\n{word}")
        for a in analyses:
            print(f"  {a['lemma']} -> {' + '.join(a['chain']) or 'ROOT'} "
                  f"[score={a['score']:.3f}]")

# ===========================================================================
# v5.3.4 — Integrated Candidate Generation
# ===========================================================================

@dataclass(frozen=True)
class RootSeedV534:
    lemma: str
    base_cost: float
    source: str


@dataclass(frozen=True)
class ForwardNodeV534:
    state: MorphState
    lemma: str
    surface: str
    features: Tuple[str, ...] = ()
    realizations: Tuple[Realization, ...] = ()
    score: float = 0.0
    notes: Tuple[str, ...] = ()


class TurkishMorphologyV534:
    """
    v5.3.4 integrates inverse morphophonology into root seeding and then
    performs constrained forward surface generation through the state graph.

    The parser does not need every intermediate underlying form to literally
    be a prefix of the surface word: a later vowel-initial suffix can alter the
    immediately preceding stem/morpheme boundary (kitap+ı -> kitabı,
    gelecek+im -> geleceğim, geldik+im -> geldiğim).
    """

    # Surface allomorph inventory.  This is candidate generation, not ranking.
    ALLOMORPHS: Dict[str, Tuple[str, ...]] = {
        "PLURAL": ("lar", "ler"),
        "POSS_1SG": ("ım", "im", "um", "üm", "m"),
        "POSS_2SG": ("ın", "in", "un", "ün", "n"),
        "POSS_3SG": ("ı", "i", "u", "ü", "sı", "si", "su", "sü"),
        "POSS_1PL": ("ımız", "imiz", "umuz", "ümüz", "mız", "miz", "muz", "müz"),
        "POSS_2PL": ("ınız", "iniz", "unuz", "ünüz", "nız", "niz", "nuz", "nüz"),
        # After an explicit plural marker, 3PL possessive can surface as -I;
        # the full -lArI forms are retained as candidates as well.
        "POSS_3PL": ("ları", "leri", "ı", "i", "u", "ü"),
        "DATIVE": ("a", "e", "ya", "ye", "na", "ne"),
        "LOCATIVE": ("da", "de", "ta", "te", "nda", "nde"),
        "ABLATIVE": ("dan", "den", "tan", "ten", "ndan", "nden"),
        "GENITIVE": ("ın", "in", "un", "ün", "nın", "nin", "nun", "nün"),
        "ACCUSATIVE": ("ı", "i", "u", "ü", "yı", "yi", "yu", "yü", "nı", "ni", "nu", "nü"),
        "COMITATIVE": ("la", "le", "yla", "yle"),
        "RELATIVE_KI": ("ki",),

        "NEGATION": ("ma", "me"),
        "NEGATIVE_ABILITY": ("yama", "yeme", "ama", "eme"),
        "ABILITY": ("yabil", "yebil", "abil", "ebil"),
        "PROGRESSIVE": ("ıyor", "iyor", "uyor", "üyor", "yor"),
        "FUTURE": ("yacak", "yecek", "acak", "ecek"),
        "PAST": ("dı", "di", "du", "dü", "tı", "ti", "tu", "tü"),
        "EVIDENTIAL": ("mış", "miş", "muş", "müş"),

        "PARTICIPLE_PRESENT": ("an", "en", "yan", "yen"),
        "PARTICIPLE_PAST": ("dık", "dik", "duk", "dük", "tık", "tik", "tuk", "tük", "mış", "miş", "muş", "müş"),
        "PARTICIPLE_FUTURE": ("yacak", "yecek", "acak", "ecek"),

        "NOMINALIZER_LIK": ("lık", "lik", "luk", "lük"),
        "NOMINALIZER_MA": ("ma", "me"),
        "DERIVATIONAL_LI": ("lı", "li"),
        "DERIVATIONAL_LU": ("lu", "lü"),
        "DERIVATIONAL_SIZ": ("sız", "siz", "suz", "süz"),
        "DERIVATIONAL_CIL": ("cıl", "cil", "cul", "cül", "çıl", "çil", "çul", "çül"),
        # Multiple candidates intentionally preserve competing analyses.
        "DERIVATIONAL_LA": ("la", "le", "laş", "leş", "laştır", "leştir"),
        "VERB_DERIVATION_LA": ("la", "le", "laş", "leş", "laştır", "leştir"),
        "INCHOATIVE_LAS": ("laş", "leş", "al", "el", "la", "le"),
        "CAUSATIVE": (
            "dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür",
            "ır", "ir", "ur", "ür", "ar", "er", "t",
            "landır", "lendir", "laştır", "leştir", "ştır", "ştir"
        ),
        "PASSIVE": ("ıl", "il", "ul", "ül", "ın", "in", "un", "ün", "n", "şıl", "şil", "şul", "şül"),

        "PERSON_1SG": ("ım", "im", "um", "üm", "m"),
        "PERSON_2SG": ("sın", "sin", "sun", "sün", "n"),
        "PERSON_1PL": ("ız", "iz", "uz", "üz", "k"),
        "PERSON_2PL": ("sınız", "siniz", "sunuz", "sünüz", "nız", "niz", "nuz", "nüz"),
        "PERSON_3PL": ("lar", "ler"),
        "PERSON_3SG": ("",),  # explicit zero morph
    }

    FEATURE_ORDER = tuple(ALLOMORPHS.keys())

    # Lexical whole-stem alternants are data, not universal deletion rules.
    WHOLE_STEM_ALTERNANTS = {
        "ağız": "ağz",
        "burun": "burn",
        "omuz": "omz",
        "karın": "karn",
        "şehir": "şehr",
        "fikir": "fikr",
        "oğul": "oğl",
    }
    INVERSE_WHOLE_STEM = {v: k for k, v in WHOLE_STEM_ALTERNANTS.items()}

    # A compact lexical inventory. Unknown roots remain productive via prefix
    # and inverse seeding, so the parser is not closed-world.
    KNOWN_ROOTS = {
        "ev","kitap","çocuk","araba","baş","güzel","sorumlu","başarısız",
        "genç","köy","tuz","yağ","akıl","renk","ağaç","ağız","burun","omuz",
        "oğul","karın","şehir","fikir","gel","git","yap","yaz","oku","anla",
        "çalış","temiz","hız","başla","karşılaştır","türkçe","türkçeleştir",
        "zengin","dar","geniş","görüş","okul","masa","bahçe","sınıf","arkadaş",
        "kanat","aç","kır","seç","anlat","göster","gül","yüz","kaz","çay","dil",
        "bin","koş","var","al","zort",
    }

    def __init__(self, roots: Optional[Iterable[str]] = None, lexicon: Optional[Lexicon] = None):
        self.grammar = TransitionGrammar()
        self.lexicon = lexicon or Lexicon()
        self.inverse_phono = InverseMorphophonology(self.lexicon)
        self.roots = set(self.KNOWN_ROOTS)
        if roots:
            self.roots.update(x.lower() for x in roots)
        self.roots.update(self.lexicon.entries.keys())
        self._harden_transitions()

    def _harden_transitions(self):
        # Productive nominal derivation can iterate (zort+lu+luk etc.).
        for f in ("NOMINALIZER_LIK", "NOMINALIZER_MA", "DERIVATIONAL_LI",
                  "DERIVATIONAL_LU", "DERIVATIONAL_SIZ", "DERIVATIONAL_CIL"):
            self.grammar.add(MorphState.DERIVED_NOMINAL, f, MorphState.DERIVED_NOMINAL, 0.18)

        # A derived verb can nominalize.
        for f in ("NOMINALIZER_LIK", "NOMINALIZER_MA"):
            self.grammar.add(MorphState.DERIVED_VERBAL, f, MorphState.DERIVED_NOMINAL, 0.18)

        # v5.2/gold terminology compatibility: verbal -lA derivation.
        self.grammar.add(MorphState.ROOT, "VERB_DERIVATION_LA", MorphState.DERIVED_VERBAL, 0.16)
        self.grammar.add(MorphState.DERIVED_NOMINAL, "VERB_DERIVATION_LA", MorphState.DERIVED_VERBAL, 0.16)
        self.grammar.add(MorphState.DERIVED_VERBAL, "VERB_DERIVATION_LA", MorphState.DERIVED_VERBAL, 0.18)

        # Modal/polarity material can feed nonfinite morphology.
        for f in ("PARTICIPLE_PRESENT", "PARTICIPLE_PAST", "PARTICIPLE_FUTURE"):
            self.grammar.add(MorphState.FINITE_TAM, f, MorphState.NONFINITE, 0.18)

        # Relational -ki can follow a cased nominal; plural/case can continue.
        self.grammar.add(MorphState.RELATIONAL, "POSS_1SG", MorphState.POSSESSED, 0.18)
        self.grammar.add(MorphState.RELATIONAL, "POSS_2SG", MorphState.POSSESSED, 0.18)
        self.grammar.add(MorphState.RELATIONAL, "POSS_3SG", MorphState.POSSESSED, 0.18)
        self.grammar.add(MorphState.RELATIONAL, "POSS_1PL", MorphState.POSSESSED, 0.18)
        self.grammar.add(MorphState.RELATIONAL, "POSS_2PL", MorphState.POSSESSED, 0.18)
        self.grammar.add(MorphState.RELATIONAL, "POSS_3PL", MorphState.POSSESSED, 0.18)

    @staticmethod
    def _is_vowel_initial(suffix: str) -> bool:
        return bool(suffix) and suffix[0] in VOWELS

    def _first_boundary_stem(self, lemma: str, suffix: str, feature: str) -> Tuple[str, Tuple[str, ...]]:
        """Lexical stem realization before the first suffix."""
        changes = []
        stem = lemma
        if not suffix:
            return stem, tuple(changes)

        softening_triggers = {
            "POSS_1SG","POSS_2SG","POSS_3SG","POSS_1PL","POSS_2PL","POSS_3PL",
            "DATIVE","ACCUSATIVE","GENITIVE"
        }
        if self._is_vowel_initial(suffix) and feature in softening_triggers:
            if lemma in self.WHOLE_STEM_ALTERNANTS:
                new = self.WHOLE_STEM_ALTERNANTS[lemma]
                changes.append(f"LEXICAL_VOWEL_DROP:{lemma}->{new}")
                stem = new
            elif stem.endswith("nk"):
                new = stem[:-1] + "g"
                changes.append(f"NK_TO_NG:{stem}->{new}")
                stem = new
            elif stem and stem[-1] in {"p","ç","t","k"}:
                mp = {"p":"b", "ç":"c", "t":"d", "k":"ğ"}
                new = stem[:-1] + mp[stem[-1]]
                changes.append(f"FINAL_STOP_VOICING:{stem}->{new}")
                stem = new
        return stem, tuple(changes)

    def _later_boundary_stem(self, surface_stem: str, suffix: str, feature: str, previous_feature: Optional[str]) -> Tuple[str, Tuple[str, ...]]:
        """Morphophonology at later morpheme boundaries."""
        stem = surface_stem
        changes = []
        if not suffix:
            return stem, tuple(changes)

        # Progressive causes deletion of the final vowel of -mA / -(y)AmA.
        if suffix in ("ıyor", "iyor", "uyor", "üyor", "yor") and stem.endswith(("ma", "me")):
            new = stem[:-1]
            changes.append(f"PRE_PROGRESSIVE_VOWEL_DROP:{stem}->{new}")
            stem = new

        # Later boundary voicing is not universal: it is especially needed
        # after FUTURE/PARTICIPLE_PAST before vowel-initial agreement/possession.
        later_softening_prev = {"FUTURE", "PARTICIPLE_FUTURE", "PARTICIPLE_PAST"}
        later_softening_next = {
            "PERSON_1SG","PERSON_2SG","PERSON_1PL","PERSON_2PL",
            "POSS_1SG","POSS_2SG","POSS_3SG","POSS_1PL","POSS_2PL","POSS_3PL",
            "DATIVE","ACCUSATIVE","GENITIVE"
        }
        if (self._is_vowel_initial(suffix) and stem and
                previous_feature in later_softening_prev and feature in later_softening_next):
            if stem.endswith("nk"):
                new = stem[:-1] + "g"
                changes.append(f"NK_TO_NG:{stem}->{new}")
                stem = new
            elif stem[-1] in {"p","ç","t","k"}:
                mp = {"p":"b", "ç":"c", "t":"d", "k":"ğ"}
                new = stem[:-1] + mp[stem[-1]]
                changes.append(f"BOUNDARY_VOICING:{stem}->{new}")
                stem = new
        return stem, tuple(changes)

    def _root_seeds(self, word: str) -> List[RootSeedV534]:
        w = word.lower()
        seeds: Dict[str, RootSeedV534] = {}

        def add(lemma: str, cost: float, source: str):
            lemma = lemma.lower()
            if len(lemma) < 2:
                return
            old = seeds.get(lemma)
            item = RootSeedV534(lemma, cost, source)
            if old is None or cost < old.base_cost:
                seeds[lemma] = item

        # Known lexical roots whose first two characters are compatible.
        for root in self.roots:
            if w.startswith(root) or w[:2] == root[:2]:
                add(root, 0.0, "known_root")

        # Productive unknown-root prefixes. Longer unknown strings receive a
        # mild over-extension penalty rather than being blindly preferred.
        for i in range(2, len(w)):
            pref = w[:i]
            cost = 1.05 + max(0, len(pref) - 6) * 0.12
            add(pref, cost, "surface_prefix")

        # Explicit whole-stem inverse alternants.
        for surface, lemma in self.INVERSE_WHOLE_STEM.items():
            if w.startswith(surface):
                add(lemma, 0.05, "inverse_whole_stem")

        # Generic/lexical inverse recovery at every plausible first boundary.
        all_surfaces = sorted({s for vals in self.ALLOMORPHS.values() for s in vals if s}, key=len, reverse=True)
        for i in range(2, len(w)):
            surface_stem = w[:i]
            remaining = w[i:]
            for suff in all_surfaces:
                if not remaining.startswith(suff):
                    continue
                # Existing inverse engine.
                for cand in self.inverse_phono.recover(surface_stem, suff):
                    add(cand.lemma, 0.10 + cand.cost, "inverse_morphophonology")
                # Generic final-stop inverse beyond the small lexicon.
                if suff[0] in VOWELS and surface_stem:
                    inv = {"b":"p", "c":"ç", "d":"t", "ğ":"k", "g":"k"}
                    if surface_stem[-1] in inv:
                        add(surface_stem[:-1] + inv[surface_stem[-1]], 0.75, "generic_inverse_stop")

        # Whole word root survives, but long opaque roots are penalized so
        # productive analyses can outrank them.
        add(w, 0.35 if len(w) <= 5 else 4.5, "whole_word")
        return sorted(seeds.values(), key=lambda x: (x.base_cost, len(x.lemma)))

    @staticmethod
    def _compatible_intermediate(surface: str, target: str) -> bool:
        if target.startswith(surface):
            return True
        # The next vowel-initial suffix may voice a final stop.
        if surface and surface[-1] in "pçtk" and target.startswith(surface[:-1]):
            return True
        # Progressive may delete the last a/e of a polarity/modality morph.
        if surface.endswith(("ma", "me")) and target.startswith(surface[:-1]):
            return True
        return False

    def _allowed_features(self, node: ForwardNodeV534) -> List[Transition]:
        return self.grammar.transitions.get(node.state, [])

    def _surfaces_for(self, node: ForwardNodeV534, feature: str) -> Tuple[str, ...]:
        if feature == "POSS_3PL":
            if node.state == MorphState.NUMBERED:
                return ("ı", "i", "u", "ü")
            if node.state == MorphState.NONFINITE:
                return ("ları", "leri")
        if feature == "CAUSATIVE" and node.state == MorphState.ROOT and node.lemma.endswith(
            ("dır","dir","dur","dür","tır","tir","tur","tür","laştır","leştir","landır","lendir")
        ):
            # Lexically causativized lemmas may retain derivational history as
            # a zero surface feature. This is an alternative candidate only.
            return self.ALLOMORPHS[feature] + ("",)
        return self.ALLOMORPHS.get(feature, ())

    def _transition_cost(self, feature: str, surface: str, root_known: bool) -> float:
        # Small additive costs preserve productive morphology over opaque roots.
        if feature == "PERSON_3SG" and surface == "":
            return 0.01
        if feature.startswith("PERSON_"):
            return 0.04
        if feature in ("PAST", "FUTURE", "PROGRESSIVE", "EVIDENTIAL"):
            return 0.12
        if feature.startswith("PARTICIPLE_"):
            return 0.16
        if feature in ("ABILITY", "NEGATIVE_ABILITY", "NEGATION"):
            return 0.14
        return 0.16

    def parse(self, word: str, max_nodes: int = 8000) -> MorphologicalLattice:
        target = word.lower()
        lattice = MorphologicalLattice()
        frontier: List[ForwardNodeV534] = []

        for seed in self._root_seeds(target):
            frontier.append(ForwardNodeV534(
                state=MorphState.ROOT,
                lemma=seed.lemma,
                surface=seed.lemma,
                score=seed.base_cost,
                notes=(seed.source,),
            ))

        seen: Dict[Tuple, float] = {}
        finals: List[ForwardNodeV534] = []
        steps = 0

        while frontier and steps < max_nodes:
            # Best-first expansion controls overgeneration.
            frontier.sort(key=lambda n: (n.score, -len(n.surface), len(n.features)))
            node = frontier.pop(0)
            steps += 1

            key = (node.state, node.lemma, node.surface, node.features)
            if key in seen and seen[key] <= node.score:
                continue
            seen[key] = node.score

            # Mirror nodes into the public lattice structure.
            lattice.add(ParseNode(
                state=node.state,
                position=min(len(node.surface), len(target)),
                lemma=node.lemma,
                surface=target,
                features=node.features,
                realizations=node.realizations,
                score=node.score,
                notes=node.notes + (f"generated={node.surface}",),
            ))

            if node.surface == target:
                # Finite TAM must carry agreement; 3SG is an explicit ZERO
                # morph rather than a competing bare finite analysis.
                if node.state != MorphState.FINITE_TAM:
                    finals.append(node)
                if node.state == MorphState.FINITE_TAM:
                    frontier.append(ForwardNodeV534(
                        state=MorphState.COMPLETE,
                        lemma=node.lemma,
                        surface=node.surface,
                        features=node.features + ("PERSON_3SG",),
                        realizations=node.realizations + (Realization("PERSON_3SG", ""),),
                        score=node.score + 0.01,
                        notes=node.notes + ("ZERO_PERSON_3SG",),
                    ))
                continue

            # If current surface cannot possibly be repaired by the next
            # boundary, stop expanding this branch.
            if node.features and not self._compatible_intermediate(node.surface, target):
                continue

            for tr in self._allowed_features(node):
                feature = tr.feature
                if feature == "COMPLETE":
                    continue
                surfaces = self._surfaces_for(node, feature)
                if not surfaces:
                    continue

                for suffix in surfaces:
                    # Zero 3SG is only meaningful when no surface remains.
                    if suffix == "" and feature == "PERSON_3SG" and node.surface != target:
                        continue

                    if not node.features:
                        stem_surface, changes = self._first_boundary_stem(node.lemma, suffix, feature)
                    else:
                        stem_surface, changes = self._later_boundary_stem(node.surface, suffix, feature, node.features[-1] if node.features else None)

                    new_surface = stem_surface + suffix
                    if len(new_surface) > len(target) + 1:
                        continue
                    if new_surface != target and not self._compatible_intermediate(new_surface, target):
                        continue

                    cost = node.score + self._transition_cost(feature, suffix, node.lemma in self.roots)
                    realization = Realization(feature, suffix, changes)
                    frontier.append(ForwardNodeV534(
                        state=tr.dst,
                        lemma=node.lemma,
                        surface=new_surface,
                        features=node.features + (feature,),
                        realizations=node.realizations + (realization,),
                        score=cost,
                        notes=node.notes + changes,
                    ))

        # Add explicit complete nodes for final candidates.
        for n in finals:
            lattice.add(ParseNode(
                state=MorphState.COMPLETE,
                position=len(target),
                lemma=n.lemma,
                surface=target,
                features=n.features,
                realizations=n.realizations,
                score=n.score,
                notes=n.notes + ("surface_exact",),
            ))
        return lattice

    def analyze(self, word: str, n_best: int = 20) -> List[ParseResult]:
        lattice = self.parse(word)
        uniq: Dict[Tuple[str, Tuple[str, ...]], ParseResult] = {}
        for n in lattice.nodes:
            if n.state != MorphState.COMPLETE or n.position != len(word.lower()):
                continue
            key = (n.lemma, n.features)
            item = ParseResult(
                lemma=n.lemma,
                features=n.features,
                realizations=n.realizations,
                state=MorphState.COMPLETE,
                score=n.score,
                complete=True,
                notes=n.notes,
            )
            old = uniq.get(key)
            if old is None or item.score < old.score:
                uniq[key] = item

        results = list(uniq.values())
        # Prefer known lexical roots and analyses that actually expose
        # morphology; do not reward long opaque unknown roots.
        results.sort(key=lambda r: (
            r.score,
            0 if r.lemma in self.roots else 1,
            0 if r.features else 1,
            len(r.features),
            len(r.lemma),
        ))
        return results[:n_best]


class TurkishMorphDisambiguatorV534:
    def __init__(self, parser: Optional[TurkishMorphologyV534] = None):
        self.parser = parser or TurkishMorphologyV534()

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        return self.parser.analyze(word, n_best=n_best)


# Compatibility aliases: the strict scorer deliberately looks for V53 names.
TurkishMorphologyV53 = TurkishMorphologyV534
TurkishMorphDisambiguatorV53 = TurkishMorphDisambiguatorV534



# ===========================================================================
# v5.4 — Gold-independent structural disambiguation / ranking
# ===========================================================================

@dataclass(frozen=True)
class RankingDecisionV54:
    structural_score: float
    adjustment: float
    total_score: float
    reasons: Tuple[str, ...] = ()


class TurkishMorphDisambiguatorV54:
    """
    Gold-independent ranking layer over v5.3.4's candidate lattice.

    No benchmark label is consulted. Ranking uses only:
      - lexical-category compatibility,
      - finite/nonfinite well-formedness,
      - suffix realization specificity,
      - compositionality / anti-bundling,
      - productive unknown-root priors.
    Lower score is better.
    """

    CLEAR_NOUNS = {
        "ev","kitap","çocuk","araba","baş","köy","tuz","yağ","renk","ağaç",
        "ağız","burun","omuz","oğul","karın","şehir","fikir","okul","masa",
        "bahçe","sınıf","arkadaş","kanat","çay","dil","hız",
    }

    CLEAR_ADJECTIVES = {
        "güzel","sorumlu","başarısız","genç","akıl","temiz","zengin","dar","geniş",
    }

    CLEAR_VERBS = {
        "gel","git","yap","yaz","oku","anla","çalış","başla","karşılaştır",
        "türkçeleştir","görüş","aç","kır","seç","anlat","göster","gül","yüz",
        "kaz","bin","koş","al",
    }

    FINITE_TAM = {"PAST","FUTURE","PROGRESSIVE","EVIDENTIAL"}
    CASE_FEATURES = {
        "DATIVE","LOCATIVE","ABLATIVE","GENITIVE","ACCUSATIVE","COMITATIVE"
    }

    def __init__(self, parser: Optional[TurkishMorphologyV534] = None):
        self.parser = parser or TurkishMorphologyV534()

    def lexical_category(self, lemma: str) -> str:
        lemma = lemma.lower()
        if lemma in self.CLEAR_VERBS:
            return "VERB"
        if lemma in self.CLEAR_ADJECTIVES:
            return "ADJ"
        if lemma in self.CLEAR_NOUNS:
            return "NOUN"
        return "UNKNOWN"

    def _decision(self, word: str, result: ParseResult) -> RankingDecisionV54:
        fs = list(result.features)
        rs = list(result.realizations)
        category = self.lexical_category(result.lemma)
        adj = 0.0
        reasons = []

        # 1) POS compatibility.
        if fs and category in {"NOUN", "ADJ"} and fs[0] == "PASSIVE":
            adj += 1.25
            reasons.append("PENALTY:DIRECT_PASSIVE_ON_NONVERB")

        if len(fs) == 1 and fs[0] == "COMITATIVE" and category == "ADJ":
            adj += 0.45
            reasons.append("PENALTY:COMITATIVE_ON_ADJECTIVE")

        # 2) Finite agreement requires finite TAM.
        for i, feature in enumerate(fs):
            if feature.startswith("PERSON_"):
                if not any(x in self.FINITE_TAM for x in fs[:i]):
                    adj += 1.50
                    reasons.append("PENALTY:PERSON_WITHOUT_FINITE_TAM")

        # 3) Nonfinite constraints.
        for i, feature in enumerate(fs):
            if feature.startswith("PARTICIPLE_"):
                if any(x.startswith("PERSON_") for x in fs[i + 1:]):
                    adj += 1.00
                    reasons.append("PENALTY:PERSON_AFTER_PARTICIPLE")

                if feature == "PARTICIPLE_PAST" and i < len(rs):
                    surf = rs[i].surface
                    if surf in {
                        "dık","dik","duk","dük","tık","tik","tuk","tük"
                    } and i == len(fs) - 1:
                        adj += 0.35
                        reasons.append("PENALTY:BARE_DIK_PARTICIPLE")

        # 4) Surface realization specificity / anti-bundling.
        for i, real in enumerate(rs):
            morph = real.morph
            surf = real.surface

            if morph == "DERIVATIONAL_LA":
                if surf not in ("la", "le"):
                    adj += 0.75
                    reasons.append("PENALTY:BUNDLED_GENERIC_LA")
                else:
                    adj += 0.06
                    reasons.append("PENALTY:GENERIC_LA_LABEL")

            elif morph == "VERB_DERIVATION_LA":
                if surf not in ("la", "le"):
                    adj += 0.65
                    reasons.append("PENALTY:BUNDLED_VERBALIZER_LA")
                elif (
                    category == "ADJ"
                    and i + 1 < len(rs)
                    and rs[i + 1].morph == "CAUSATIVE"
                    and rs[i + 1].surface == "t"
                ):
                    adj += 0.18
                    reasons.append("PENALTY:ADJ_LA_PLUS_CAUSATIVE")

            elif morph == "INCHOATIVE_LAS":
                if surf in ("laş", "leş"):
                    adj -= 0.08
                    reasons.append("BONUS:CANONICAL_INCHOATIVE_LAS")
                elif (
                    surf in ("la", "le")
                    and category == "ADJ"
                    and i + 1 < len(rs)
                    and rs[i + 1].morph == "CAUSATIVE"
                    and rs[i + 1].surface == "t"
                ):
                    adj -= 0.04
                    reasons.append("BONUS:ADJ_INCHOATIVE_BEFORE_CAUSATIVE")
                else:
                    adj += 0.55
                    reasons.append("PENALTY:NONCANONICAL_INCHOATIVE")

            elif morph == "CAUSATIVE":
                if surf == "":
                    adj += 0.45
                    reasons.append("PENALTY:ZERO_CAUSATIVE")
                elif surf in ("laştır", "leştir"):
                    adj += 0.50
                    reasons.append("PENALTY:BUNDLED_CAUSATIVE")

            elif (
                morph == "POSS_3PL"
                and surf in ("ları", "leri")
                and category == "NOUN"
            ):
                try:
                    idx = fs.index("POSS_3PL")
                except ValueError:
                    idx = -1
                if idx >= 0 and any(
                    x in self.CASE_FEATURES for x in fs[idx + 1:]
                ):
                    adj += 0.22
                    reasons.append("PENALTY:BUNDLED_3PL_POSSESSIVE")

        # 5) Unknown-root productivity.
        if category == "UNKNOWN" and len(fs) == 1:
            if fs[0] == "VERB_DERIVATION_LA":
                adj -= 0.03
                reasons.append("BONUS:UNKNOWN_PRODUCTIVE_VERBALIZER")
            elif fs[0] == "COMITATIVE":
                adj += 0.03
                reasons.append("PENALTY:UNKNOWN_COMITATIVE_PRIOR")

        if (
            len(rs) >= 2
            and rs[0].morph == "INCHOATIVE_LAS"
            and rs[0].surface in ("laş", "leş")
            and rs[1].morph == "CAUSATIVE"
        ):
            adj -= 0.08
            reasons.append("BONUS:COMPOSITIONAL_INCHOATIVE_CAUSATIVE")

        return RankingDecisionV54(
            structural_score=result.score,
            adjustment=adj,
            total_score=result.score + adj,
            reasons=tuple(reasons),
        )

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        candidates = self.parser.analyze(word, n_best=n_best)
        ranked = sorted(
            enumerate(candidates),
            key=lambda item: (
                self._decision(word, item[1]).total_score,
                item[0],
            ),
        )
        return [cand for _, cand in ranked][:n_best]

    def explain_word(self, word: str, n_best: int = 10) -> List[dict]:
        candidates = self.parser.analyze(word, n_best=max(n_best, 20))
        rows = []
        for original_rank, cand in enumerate(candidates, start=1):
            d = self._decision(word, cand)
            rows.append({
                "original_rank": original_rank,
                "lemma": cand.lemma,
                "chain": list(cand.features),
                "structural_score": cand.score,
                "adjustment": d.adjustment,
                "v54_score": d.total_score,
                "reasons": list(d.reasons),
                "realizations": [
                    {"morph": r.morph, "surface": r.surface}
                    for r in cand.realizations
                ],
            })
        rows.sort(key=lambda x: (x["v54_score"], x["original_rank"]))
        for i, row in enumerate(rows, start=1):
            row["v54_rank"] = i
        return rows[:n_best]


TurkishMorphologyV53 = TurkishMorphologyV534
TurkishMorphDisambiguatorV53 = TurkishMorphDisambiguatorV54


# ===========================================================================
# v5.4.1 — Contextual Disambiguator
# ===========================================================================

@dataclass(frozen=True)
class ContextualTokenChoice:
    surface: str
    lemma: str
    features: Tuple[str, ...]
    local_score: float
    contextual_adjustment: float
    total_contribution: float
    reasons: Tuple[str, ...] = ()


@dataclass
class ContextualSentenceAnalysis:
    sentence: str
    tokens: List[str]
    choices: List[ContextualTokenChoice]
    score: float

    def as_dict(self) -> dict:
        return {
            "sentence": self.sentence,
            "tokens": self.tokens,
            "score": self.score,
            "choices": [
                {
                    "surface": c.surface,
                    "lemma": c.lemma,
                    "features": list(c.features),
                    "local_score": c.local_score,
                    "contextual_adjustment": c.contextual_adjustment,
                    "total_contribution": c.total_contribution,
                    "reasons": list(c.reasons),
                }
                for c in self.choices
            ],
        }


class TurkishContextualDisambiguatorV541(TurkishMorphDisambiguatorV54):
    """
    Sentence-level, gold-independent contextual disambiguator.

    v5.4's word-internal structural ranking remains the local prior.
    v5.4.1 adds contextual evidence from:
      * closed-class lexical items,
      * genitive -> possessive constructions,
      * genitive pronoun -> matching possessive agreement,
      * accusative object -> transitive finite verb preference,
      * subject pronoun -> finite person agreement,
      * finite vs participial use from sentence position / following nominal,
      * sentence-final finite-predicate preference.

    The model is intentionally rule-based and inspectable.  It does not look
    at benchmark gold labels and does not alter the morphological grammar.
    """

    TOKEN_RE = re.compile(
        r"[A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû]+(?:'[A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû]+)?",
        re.UNICODE,
    )

    CLOSED_CLASS = {
        # Pronouns / determiners
        "ben": "PRON", "sen": "PRON", "o": "PRON", "biz": "PRON",
        "siz": "PRON", "onlar": "PRON", "bu": "DET", "şu": "DET",
        "bir": "DET", "bazı": "DET", "her": "DET", "hiçbir": "DET",

        # Genitive pronouns are useful directly for possession agreement.
        "benim": "PRON_GEN", "senin": "PRON_GEN", "onun": "PRON_GEN",
        "bizim": "PRON_GEN", "sizin": "PRON_GEN", "onların": "PRON_GEN",

        # Common function/adverbial items.
        "çok": "ADV", "yeniden": "ADV", "yine": "ADV", "hemen": "ADV",
        "artık": "ADV", "bugün": "ADV", "yarın": "ADV", "sonra": "ADV",
        "önce": "ADV", "de": "PART", "da": "PART", "ve": "CONJ",
        "ama": "CONJ", "ile": "POSTP", "için": "POSTP",
    }

    SUBJECT_PERSON = {
        "ben": "PERSON_1SG",
        "sen": "PERSON_2SG",
        "o": "PERSON_3SG",
        "biz": "PERSON_1PL",
        "siz": "PERSON_2PL",
        "onlar": "PERSON_3PL",
    }

    GENITIVE_PRONOUN_TO_POSS = {
        "benim": "POSS_1SG",
        "senin": "POSS_2SG",
        "onun": "POSS_3SG",
        "bizim": "POSS_1PL",
        "sizin": "POSS_2PL",
        "onların": "POSS_3PL",
    }

    # This is a conservative lexical valency prior, not a hard grammar rule.
    TRANSITIVE_VERBS = {
        "oku", "yaz", "gör", "bil", "dene", "anla", "seç", "karşılaştır",
        "temizle", "aç", "kapat", "incele", "bul", "al", "ver", "yap",
    }

    PARTICIPLES = {
        "PARTICIPLE_PRESENT", "PARTICIPLE_PAST", "PARTICIPLE_FUTURE"
    }

    def __init__(
        self,
        parser: Optional[TurkishMorphologyV534] = None,
        beam_width: int = 96,
        candidates_per_token: int = 20,
    ):
        super().__init__(parser=parser)
        self.beam_width = beam_width
        self.candidates_per_token = candidates_per_token

    # ------------------------------------------------------------------
    # Public compatibility: context-free word scoring stays identical to v5.4.
    # ------------------------------------------------------------------

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        return super().analyze_word(word, n_best=n_best)

    # ------------------------------------------------------------------
    # Token / candidate typing
    # ------------------------------------------------------------------

    @staticmethod
    def _lower(s: str) -> str:
        # Python's lower handles Turkish letters well enough for our explicit
        # lexical lists except dotted I edge cases; normalize the common one.
        return s.replace("İ", "i").lower()

    def tokenize(self, sentence: str) -> List[str]:
        return self.TOKEN_RE.findall(sentence)

    def _is_finite(self, a: ParseResult) -> bool:
        fs = set(a.features)
        return bool(fs & self.FINITE_TAM) and any(
            f.startswith("PERSON_") for f in fs
        )

    def _is_participle(self, a: ParseResult) -> bool:
        return any(f in self.PARTICIPLES for f in a.features)

    def _is_nominal(self, surface: str, a: ParseResult) -> bool:
        w = self._lower(surface)
        if w in self.CLOSED_CLASS:
            return self.CLOSED_CLASS[w] in {"DET", "PRON", "PRON_GEN"}
        if self._is_finite(a):
            return False
        if self._is_participle(a):
            return True
        cat = self.lexical_category(a.lemma)
        if cat in {"NOUN", "ADJ"}:
            return True
        nominal_marks = {
            "PLURAL", "POSS_1SG", "POSS_2SG", "POSS_3SG",
            "POSS_1PL", "POSS_2PL", "POSS_3PL",
            "DATIVE", "LOCATIVE", "ABLATIVE", "GENITIVE",
            "ACCUSATIVE", "COMITATIVE", "RELATIVE_KI",
            "NOMINALIZER_LIK", "NOMINALIZER_MA",
        }
        return bool(set(a.features) & nominal_marks) or not a.features

    def _person(self, a: ParseResult) -> Optional[str]:
        for f in a.features:
            if f.startswith("PERSON_"):
                return f
        return None

    def _possessive(self, a: ParseResult) -> Optional[str]:
        for f in a.features:
            if f.startswith("POSS_"):
                return f
        return None

    # ------------------------------------------------------------------
    # Context scoring
    # ------------------------------------------------------------------

    def _context_unary(
        self,
        tokens: Sequence[str],
        i: int,
        a: ParseResult,
    ) -> Tuple[float, Tuple[str, ...]]:
        word = self._lower(tokens[i])
        fs = list(a.features)
        adj = 0.0
        reasons = []

        # A closed-class item should normally remain lexical rather than be
        # spuriously segmented by productive morphology.
        if word in self.CLOSED_CLASS:
            if self._lower(a.lemma) == word and not fs:
                adj -= 4.00
                reasons.append("CTX_BONUS:CLOSED_CLASS_LEXICAL")
            elif fs:
                adj += 0.60
                reasons.append("CTX_PENALTY:CLOSED_CLASS_MORPH_ANALYSIS")

        # Explicit genitive pronoun controls possessive agreement on the next
        # nominal. This uses the raw word form, not benchmark labels.
        if i > 0:
            prev = self._lower(tokens[i - 1])
            expected = self.GENITIVE_PRONOUN_TO_POSS.get(prev)
            if expected:
                poss = self._possessive(a)
                if poss == expected:
                    adj -= 0.65
                    reasons.append("CTX_BONUS:GEN_PRONOUN_POSSESSIVE_MATCH")
                elif poss is not None:
                    adj += 0.55
                    reasons.append("CTX_PENALTY:GEN_PRONOUN_POSSESSIVE_MISMATCH")
                elif "ACCUSATIVE" in fs:
                    adj += 0.30
                    reasons.append("CTX_PENALTY:ACC_AFTER_GEN_PRONOUN")

        # Subject pronoun -> finite person agreement. Search a short window,
        # stopping at another overt pronoun.
        if self._is_finite(a):
            person = self._person(a)
            subject = None
            for j in range(i - 1, max(-1, i - 4), -1):
                wj = self._lower(tokens[j])
                if wj in self.SUBJECT_PERSON:
                    subject = self.SUBJECT_PERSON[wj]
                    break
            if subject and person:
                if subject == person:
                    adj -= 0.35
                    reasons.append("CTX_BONUS:SUBJECT_PERSON_MATCH")
                else:
                    adj += 0.55
                    reasons.append("CTX_PENALTY:SUBJECT_PERSON_MISMATCH")

        # Sentence-final morphology strongly favors a finite predicate when
        # the competing analysis is participial. Do not penalize adjectives/
        # nouns generally; this only targets finite/nonfinite ambiguity.
        if i == len(tokens) - 1:
            if self._is_finite(a):
                adj -= 0.18
                reasons.append("CTX_BONUS:SENTENCE_FINAL_FINITE")
            elif self._is_participle(a):
                adj += 0.16
                reasons.append("CTX_PENALTY:SENTENCE_FINAL_PARTICIPLE")

        return adj, tuple(reasons)

    def _pair_score(
        self,
        left_surface: str,
        left: ParseResult,
        right_surface: str,
        right: ParseResult,
    ) -> Tuple[float, Tuple[str, ...]]:
        lf = list(left.features)
        rf = list(right.features)
        adj = 0.0
        reasons = []

        # Genitive + possessive nominal construction:
        # kitabın kapağı, evin kitabı, ...
        if "GENITIVE" in lf:
            poss = self._possessive(right)
            if poss is not None and self._is_nominal(right_surface, right):
                adj -= 0.55
                reasons.append("CTX_BONUS:GENITIVE_POSSESSIVE_CONSTRUCTION")
            elif self._is_nominal(right_surface, right):
                adj += 0.10
                reasons.append("CTX_PENALTY:GENITIVE_WITHOUT_POSSESSIVE_HEAD")

        # Accusative object directly before a finite transitive predicate.
        if "ACCUSATIVE" in lf and self._is_finite(right):
            if self._lower(right.lemma) in self.TRANSITIVE_VERBS:
                adj -= 0.52
                reasons.append("CTX_BONUS:ACCUSATIVE_BEFORE_TRANSITIVE_VERB")
            else:
                adj -= 0.14
                reasons.append("CTX_BONUS:ACCUSATIVE_BEFORE_FINITE_VERB")

        # A possessive reading directly before a clear transitive finite verb
        # is possible ("kitabı geldi" etc. with another syntax), so only use a
        # mild competing prior rather than forbidding it.
        if (
            self._possessive(left) is not None
            and self._is_finite(right)
            and self._lower(right.lemma) in self.TRANSITIVE_VERBS
        ):
            adj += 0.10
            reasons.append("CTX_PENALTY:POSSESSIVE_BEFORE_TRANSITIVE_VERB")

        # Finite vs participle: before a nominal head, participial reading is
        # preferred; finite reading is dispreferred.
        if self._is_nominal(right_surface, right):
            if self._is_participle(left):
                adj -= 0.34
                reasons.append("CTX_BONUS:PARTICIPLE_BEFORE_NOMINAL")
            elif self._is_finite(left):
                adj += 0.24
                reasons.append("CTX_PENALTY:FINITE_BEFORE_NOMINAL")

        return adj, tuple(reasons)

    # ------------------------------------------------------------------
    # Sentence decoding
    # ------------------------------------------------------------------

    def _raw_candidates(self, word: str) -> List[ParseResult]:
        # Use the parser lattice directly so context can rescue candidates that
        # v5.4 ranks below top-1. Local v5.4 score is still used as the prior.
        return self.parser.analyze(word, n_best=self.candidates_per_token)

    def analyze_sentence(
        self,
        sentence: str,
        n_best_sentences: int = 1,
    ) -> List[ContextualSentenceAnalysis]:
        tokens = self.tokenize(sentence)
        if not tokens:
            return []

        candidate_sets = []
        for word in tokens:
            cands = self._raw_candidates(word)
            if not cands:
                # Defensive fallback should be rare because v5.3.4 has 100%
                # word coverage on the frozen benchmark.
                cands = [
                    ParseResult(
                        lemma=self._lower(word),
                        features=(),
                        realizations=(),
                        state=MorphState.COMPLETE,
                        score=9.0,
                        complete=True,
                        notes=("context_fallback",),
                    )
                ]
            candidate_sets.append(cands)

        # Beam item: (score, choices, previous ParseResult)
        beam = [(0.0, [], None)]

        for i, (surface, candidates) in enumerate(zip(tokens, candidate_sets)):
            expanded = []

            for path_score, choices, prev in beam:
                for cand in candidates:
                    local = self._decision(surface, cand).total_score
                    ctx_adj, unary_reasons = self._context_unary(tokens, i, cand)

                    pair_adj = 0.0
                    pair_reasons = ()
                    if prev is not None:
                        pair_adj, pair_reasons = self._pair_score(
                            tokens[i - 1], prev, surface, cand
                        )

                    total_adj = ctx_adj + pair_adj
                    contribution = local + total_adj
                    choice = ContextualTokenChoice(
                        surface=surface,
                        lemma=cand.lemma,
                        features=tuple(cand.features),
                        local_score=local,
                        contextual_adjustment=total_adj,
                        total_contribution=contribution,
                        reasons=tuple(unary_reasons) + tuple(pair_reasons),
                    )
                    expanded.append(
                        (path_score + contribution, choices + [choice], cand)
                    )

            expanded.sort(key=lambda x: x[0])
            beam = expanded[:self.beam_width]

        out = [
            ContextualSentenceAnalysis(
                sentence=sentence,
                tokens=tokens,
                choices=choices,
                score=score,
            )
            for score, choices, _ in beam[:n_best_sentences]
        ]
        return out

    def best_sentence(self, sentence: str) -> Optional[ContextualSentenceAnalysis]:
        analyses = self.analyze_sentence(sentence, n_best_sentences=1)
        return analyses[0] if analyses else None

    def explain_sentence(self, sentence: str) -> dict:
        best = self.best_sentence(sentence)
        return best.as_dict() if best else {
            "sentence": sentence,
            "tokens": [],
            "choices": [],
            "score": None,
        }


# Compatibility aliases:
# - word-level strict scorer calls analyze_word() and therefore remains v5.4
# - clients can use TurkishContextualDisambiguatorV541 for sentence decoding.
TurkishMorphologyV53 = TurkishMorphologyV534
TurkishMorphDisambiguatorV53 = TurkishContextualDisambiguatorV541


# ===========================================================================
# v5.5 — Real-Corpus Morphology Expansion
# P0-1 vertical slice: AORIST / HABITUAL / PRESENT-SIMPLE
# ===========================================================================

class TurkishMorphologyV55(TurkishMorphologyV534):
    """
    v5.5 architecture reserves the four P0 domains discovered from UD-BOUN.

    This first vertical slice IMPLEMENTS only AORIST. The remaining requested
    ontology labels are already present in FEATURE_ORDER but have no active
    surface rules/transitions yet, so they cannot accidentally generate parses.

    Reserved P0 labels:
      AORIST
      CONVERB
      INFINITIVE
      VERBAL_NOUN
      CONDITIONAL
      NECESSITATIVE
      OPTATIVE
      IMPERATIVE
    """

    P0_FEATURES = (
        "AORIST",
        "CONVERB",
        "INFINITIVE",
        "VERBAL_NOUN",
        "CONDITIONAL",
        "NECESSITATIVE",
        "OPTATIVE",
        "IMPERATIVE",
    )

    # Cambridge/Ketrez: monosyllabic consonant-final exceptions that take -Ir.
    AORIST_IR_MONOSYLLABIC_EXCEPTIONS = frozenset({
        "al", "bil", "bul", "dur", "gel", "gör", "kal",
        "ol", "öl", "san", "ver", "var", "vur",
    })

    KNOWN_ROOTS = set(TurkishMorphologyV534.KNOWN_ROOTS) | set(
        AORIST_IR_MONOSYLLABIC_EXCEPTIONS
    ) | {
        "uyu", "söyle",
    }

    ALLOMORPHS = dict(TurkishMorphologyV534.ALLOMORPHS)
    ALLOMORPHS.update({
        # AORIST is selected by _aorist_surface(); these are only the declared
        # possible realizations for root-seeding / introspection.
        "AORIST": ("r", "ar", "er", "ır", "ir", "ur", "ür", "z", ""),
        # Reserved for subsequent P0 slices; empty means "ontology exists,
        # generation not implemented yet".
        "CONVERB": (),
        "INFINITIVE": (),
        "VERBAL_NOUN": (),
        "CONDITIONAL": (),
        "NECESSITATIVE": (),
        "OPTATIVE": (),
        "IMPERATIVE": (),
    })
    FEATURE_ORDER = tuple(ALLOMORPHS.keys())

    def _root_seeds(self, word: str) -> List[RootSeedV534]:
        seeds = list(super()._root_seeds(word))
        w = word.lower()

        extras = []
        # ye- -> yi- before y-buffered forms: yiyip, yiyerek, yiyince.
        if w.startswith("yiy"):
            extras.append(RootSeedV534("ye", 0.0, "lexical_irregular_ye"))

        # de- -> di- specifically in diyerek; deyip/deyince keep de-.
        if w.startswith("diye"):
            extras.append(RootSeedV534("de", 0.0, "lexical_irregular_de"))

        # et -> ed- before vowel-initial verbal morphology:
        # edip, ederek, eder, edebilir, edeme...
        if w.startswith("ed"):
            extras.append(RootSeedV534("et", 0.0, "lexical_verbal_t_to_d_inverse"))

        best = {s.lemma: s for s in seeds}
        for s in extras:
            old = best.get(s.lemma)
            if old is None or s.base_cost < old.base_cost:
                best[s.lemma] = s
        return sorted(best.values(), key=lambda x: (x.base_cost, len(x.lemma)))

    def _harden_transitions(self):
        super()._harden_transitions()

        # Aorist is finite TAM. It may directly follow a verbal root or a
        # derived verbal stem, and it may follow polarity/modality material
        # already represented in FINITE_TAM (gel-me-z, yap-abil-ir).
        self.grammar.add(MorphState.ROOT, "AORIST", MorphState.FINITE_TAM, 0.10)
        self.grammar.add(MorphState.DERIVED_VERBAL, "AORIST", MorphState.FINITE_TAM, 0.10)
        self.grammar.add(MorphState.FINITE_TAM, "AORIST", MorphState.FINITE_TAM, 0.10)

    @staticmethod
    def _vowel_count(stem: str) -> int:
        return sum(ch in VOWELS for ch in stem.lower())

    @staticmethod
    def _harmonic_I(stem: str) -> str:
        v = last_vowel(stem)
        if v in "aı":
            return "ı"
        if v in "ei":
            return "i"
        if v in "ou":
            return "u"
        if v in "öü":
            return "ü"
        return "i"

    @staticmethod
    def _harmonic_A(stem: str) -> str:
        v = last_vowel(stem)
        return "e" if v in FRONT_VOWELS else "a"

    def _aorist_surface(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        """
        Positive:
          V-final -> -r
          polysyllabic C-final -> -Ir
          most monosyllabic C-final -> -Ar
          13 lexical monosyllabic exceptions -> -Ir

        Negative / negative ability:
          -mA + AORIST -> -mAz for non-1st persons
          -mA + AORIST(Ø) -> 1SG/1PL special cells
        """
        stem = node.surface
        if not stem:
            return ()

        negative_context = (
            bool(node.features)
            and node.features[-1] in {"NEGATION", "NEGATIVE_ABILITY"}
            and stem.endswith(("ma", "me"))
        )
        if negative_context:
            # 'z' handles gelmez/sin/ler; epsilon feeds gelme-m / gelme-yiz.
            return ("z", "")

        if stem[-1] in VOWELS:
            return ("r",)

        lemma = node.lemma.lower()
        if (
            self._vowel_count(stem) == 1
            and lemma not in self.AORIST_IR_MONOSYLLABIC_EXCEPTIONS
        ):
            return (self._harmonic_A(stem) + "r",)

        return (self._harmonic_I(stem) + "r",)

    def _negative_aorist_zero(self, node: ForwardNodeV534) -> bool:
        return bool(
            node.features
            and node.features[-1] == "AORIST"
            and node.realizations
            and node.realizations[-1].surface == ""
            and any(
                f in {"NEGATION", "NEGATIVE_ABILITY"}
                for f in node.features[:-1]
            )
        )

    def _allowed_features(self, node: ForwardNodeV534) -> List[Transition]:
        transitions = super()._allowed_features(node)

        # The zero allomorph of negative aorist exists only in the first
        # person cells. Prevent *gelme-Ø-Ø(3sg), *gelme-Ø-sin etc.
        if self._negative_aorist_zero(node):
            transitions = [
                t for t in transitions
                if t.feature in {"PERSON_1SG", "PERSON_1PL"}
            ]
        return transitions

    def _surfaces_for(self, node: ForwardNodeV534, feature: str) -> Tuple[str, ...]:
        if feature == "AORIST":
            return self._aorist_surface(node)

        # Negative aorist 1PL: gel-me-Ø-yiz, yap-ma-Ø-yız.
        if (
            feature == "PERSON_1PL"
            and self._negative_aorist_zero(node)
        ):
            v = self._harmonic_I(node.surface)
            return ("y" + v + "z",)

        return super()._surfaces_for(node, feature)

    def _transition_cost(self, feature: str, surface: str, root_known: bool) -> float:
        if feature == "AORIST":
            return 0.10
        return super()._transition_cost(feature, surface, root_known)

    def analyze(self, word: str, n_best: int = 20) -> List[ParseResult]:
        results = super().analyze(word, n_best=max(n_best * 2, 40))

        filtered = []
        for r in results:
            # v5.3.4 automatically adds zero PERSON_3SG to any FINITE_TAM
            # state that reaches the target surface. For negative-aorist
            # epsilon, that would create an impossible *gelme analysis.
            if (
                "AORIST" in r.features
                and "PERSON_3SG" in r.features
                and any(f in {"NEGATION", "NEGATIVE_ABILITY"} for f in r.features)
            ):
                try:
                    ai = list(r.features).index("AORIST")
                    if ai < len(r.realizations) and r.realizations[ai].surface == "":
                        continue
                except ValueError:
                    pass
            filtered.append(r)

        return filtered[:n_best]


class TurkishMorphDisambiguatorV55(TurkishMorphDisambiguatorV54):
    """
    v5.4 structural ranking + v5.5 finite AORIST awareness.
    """
    FINITE_TAM = set(TurkishMorphDisambiguatorV54.FINITE_TAM) | {"AORIST"}

    def __init__(self, parser: Optional[TurkishMorphologyV55] = None):
        self.parser = parser or TurkishMorphologyV55()

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        pool = max(60, n_best * 3)
        candidates = self.parser.analyze(word, n_best=pool)
        ranked = sorted(
            enumerate(candidates),
            key=lambda item: (
                self._decision(word, item[1]).total_score,
                item[0],
            ),
        )
        return [cand for _, cand in ranked][:n_best]

    def _decision(self, word: str, result: ParseResult) -> RankingDecisionV54:
        base = super()._decision(word, result)
        adj = base.adjustment
        reasons = list(base.reasons)

        # A canonical aorist with finite agreement is a complete finite parse,
        # not a bare derivational reading of -Ar/-Ir.
        if (
            "AORIST" in result.features
            and any(f.startswith("PERSON_") for f in result.features)
        ):
            adj -= 0.08
            reasons.append("BONUS:CANONICAL_FINITE_AORIST")

        return RankingDecisionV54(
            structural_score=base.structural_score,
            adjustment=adj,
            total_score=base.structural_score + adj,
            reasons=tuple(reasons),
        )


class TurkishContextualDisambiguatorV55(TurkishContextualDisambiguatorV541):
    """
    v5.4.1 sentence context on top of the v5.5 parser/ranker.
    """
    FINITE_TAM = set(TurkishContextualDisambiguatorV541.FINITE_TAM) | {"AORIST"}

    def __init__(
        self,
        parser: Optional[TurkishMorphologyV55] = None,
        beam_width: int = 96,
        candidates_per_token: int = 20,
    ):
        # Pass the v5.5 parser through v5.4.1's initialization path.
        super().__init__(
            parser=parser or TurkishMorphologyV55(),
            beam_width=beam_width,
            candidates_per_token=candidates_per_token,
        )

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        pool = max(60, n_best * 3)
        candidates = self.parser.analyze(word, n_best=pool)
        ranked = sorted(
            enumerate(candidates),
            key=lambda item: (
                self._decision(word, item[1]).total_score,
                item[0],
            ),
        )
        return [cand for _, cand in ranked][:n_best]

    def _raw_candidates(self, word: str) -> List[ParseResult]:
        # Sentence decoding also needs the broader pre-ranking pool after
        # ontology expansion.
        return self.parser.analyze(
            word, n_best=max(60, self.candidates_per_token * 3)
        )

    def _decision(self, word: str, result: ParseResult) -> RankingDecisionV54:
        # self is a V54 descendant through v5.4.1, so call the common V54
        # structural ranker directly, then add the same v5.5 AORIST prior.
        base = TurkishMorphDisambiguatorV54._decision(self, word, result)
        adj = base.adjustment
        reasons = list(base.reasons)
        if (
            "AORIST" in result.features
            and any(f.startswith("PERSON_") for f in result.features)
        ):
            adj -= 0.08
            reasons.append("BONUS:CANONICAL_FINITE_AORIST")
        return RankingDecisionV54(
            structural_score=base.structural_score,
            adjustment=adj,
            total_score=base.structural_score + adj,
            reasons=tuple(reasons),
        )


# Scorer/API compatibility.
TurkishMorphologyV53 = TurkishMorphologyV55
TurkishMorphDisambiguatorV53 = TurkishContextualDisambiguatorV55
# External UD evaluator v1.x looks up this historical symbol explicitly.
TurkishContextualDisambiguatorV541 = TurkishContextualDisambiguatorV55


# ===========================================================================
# v5.5 P0-2 — CONVERB vertical slice
# ===========================================================================

class TurkishMorphologyV552(TurkishMorphologyV55):
    """
    P0-2 CONVERB slice.

    Ontology:
        feature = CONVERB

    Realization subtype is preserved in Realization.changes:
        CONVERB_SUBTYPE:IP
        CONVERB_SUBTYPE:ARAK
        CONVERB_SUBTYPE:INCA
        CONVERB_SUBTYPE:KEN
        CONVERB_SUBTYPE:MADAN
        CONVERB_SUBTYPE:DIKCA

    Implemented productive paths:
        -(y)Ip
        -(y)ArAk
        -(y)IncA
        AORIST + -ken
        NEGATION / NEGATIVE_ABILITY + -DAn  => -mAdAn / -AmAdAn
        PARTICIPLE_PAST + -çA              => -DIkçA

    Ranking is intentionally unchanged.
    """

    # Declared surface inventory is broad enough for inverse root seeding.
    ALLOMORPHS = dict(TurkishMorphologyV55.ALLOMORPHS)
    ALLOMORPHS["CONVERB"] = (
        "ıp", "ip", "up", "üp", "yıp", "yip", "yup", "yüp",
        "arak", "erek", "yarak", "yerek",
        "ınca", "ince", "unca", "ünce",
        "yınca", "yince", "yunca", "yünce",
        "ken", "dan", "den", "ça", "çe",
    )
    FEATURE_ORDER = tuple(ALLOMORPHS.keys())

    # Verb-internal t~d alternation is lexical, not a general final-stop rule.
    # It is needed in the P0 surface environments:
    #   et + er -> eder, et + ip -> edip, git + ip -> gidip.
    VERBAL_T_D_VOICING_ROOTS = frozenset({"et", "git"})

    KNOWN_ROOTS = set(TurkishMorphologyV55.KNOWN_ROOTS) | {
        "et", "de", "ye", "tut", "taşı", "yay", "kes", "bük",
        "düş", "aktar", "silkin", "düşün", "belirt", "bulun", "don",
    }

    def _harden_transitions(self):
        super()._harden_transitions()

        # Simple converbs are clause-adverbial final forms in this slice.
        self.grammar.add(
            MorphState.ROOT, "CONVERB", MorphState.COMPLETE, 0.14,
            note="P0-2 simple converb"
        )
        self.grammar.add(
            MorphState.DERIVED_VERBAL, "CONVERB", MorphState.COMPLETE, 0.14,
            note="P0-2 derived-verbal converb"
        )

        # FINITE_TAM is reused by polarity/modality and by true finite TAM.
        # _converb_surfaces() strictly controls which subtypes are legal
        # for the immediately preceding feature.
        self.grammar.add(
            MorphState.FINITE_TAM, "CONVERB", MorphState.COMPLETE, 0.14,
            note="P0-2 polarity/TAM-fed converb"
        )

        # -DIkçA is represented compositionally:
        # PARTICIPLE_PAST + CONVERB(DIKCA).
        self.grammar.add(
            MorphState.NONFINITE, "CONVERB", MorphState.COMPLETE, 0.16,
            note="P0-2 participial converb"
        )

    def _direct_converb_surfaces(self, stem: str) -> Tuple[str, ...]:
        if not stem:
            return ()

        i = self._harmonic_I(stem)
        a = self._harmonic_A(stem)
        buffer = "y" if stem[-1] in VOWELS else ""

        ip = buffer + i + "p"
        arak = buffer + a + "r" + a + "k"
        inca = buffer + i + "nc" + a
        return (ip, arak, inca)

    def _converb_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        # ROOT / derived verb: direct productive converbs.
        if node.state in {MorphState.ROOT, MorphState.DERIVED_VERBAL}:
            return self._direct_converb_surfaces(node.surface)

        # Polarity/modality or finite TAM.
        if node.state == MorphState.FINITE_TAM and node.features:
            last = node.features[-1]

            # -ken after a TAM stem. AORIST is the high-frequency path
            # (gelir-ken, yapar-ken); the other forms are productive too.
            if last in {
                "AORIST", "PROGRESSIVE", "EVIDENTIAL", "FUTURE"
            }:
                return ("ken",)

            # After polarity/modality, direct converbs remain possible:
            # gelme-yip, gelme-yerek, gelme-yince,
            # yapabil-ip, okuyama-yınca...
            if last in {"NEGATION", "ABILITY", "NEGATIVE_ABILITY"}:
                vals = list(self._direct_converb_surfaces(node.surface))

                # -mAdAn / -AmAdAn: the negative material is already the
                # previous morph; CONVERB contributes only -DAn.
                if last in {"NEGATION", "NEGATIVE_ABILITY"}:
                    vals.append("den" if last_vowel(node.surface) in FRONT_VOWELS else "dan")
                return tuple(vals)

        # -DIkçA: gel-dik-çe, yap-tık-ça.
        if (
            node.state == MorphState.NONFINITE
            and node.features
            and node.features[-1] == "PARTICIPLE_PAST"
        ):
            return (
                "çe" if last_vowel(node.surface) in FRONT_VOWELS else "ça",
            )

        return ()

    def _converb_subtype(
        self,
        node: ForwardNodeV534,
        suffix: str,
    ) -> Optional[str]:
        if suffix == "ken":
            return "KEN"

        if (
            suffix in {"dan", "den"}
            and node.features
            and node.features[-1] in {"NEGATION", "NEGATIVE_ABILITY"}
        ):
            return "MADAN"

        if (
            suffix in {"ça", "çe"}
            and node.features
            and node.features[-1] == "PARTICIPLE_PAST"
        ):
            return "DIKCA"

        if suffix.endswith("p"):
            return "IP"
        if suffix.endswith(("arak", "erek")):
            return "ARAK"
        if suffix.endswith(("ınca", "ince", "unca", "ünce")):
            return "INCA"
        return None

    def _surfaces_for(self, node: ForwardNodeV534, feature: str) -> Tuple[str, ...]:
        if feature == "CONVERB":
            return self._converb_surfaces(node)
        return super()._surfaces_for(node, feature)

    def _first_boundary_stem(
        self,
        lemma: str,
        suffix: str,
        feature: str,
    ) -> Tuple[str, Tuple[str, ...]]:
        stem, changes = super()._first_boundary_stem(lemma, suffix, feature)
        changes = list(changes)

        # Lexical t->d in vowel-initial P0 environments.
        if (
            feature in {"AORIST", "CONVERB", "ABILITY", "NEGATIVE_ABILITY"}
            and suffix
            and suffix[0] in VOWELS
            and lemma in self.VERBAL_T_D_VOICING_ROOTS
            and stem.endswith("t")
        ):
            old = stem
            stem = stem[:-1] + "d"
            changes.append(f"LEXICAL_VERBAL_T_TO_D:{old}->{stem}")

        # de-/ye- have lexical y-buffer stem behavior. Only the ARAK path
        # needs de -> di here (diyerek); ye -> yi is productive before y.
        if feature == "CONVERB" and lemma == "de" and suffix == "yerek":
            old = stem
            stem = "di"
            changes.append(f"LEXICAL_DE_ARAK:{old}->{stem}")
        elif (
            feature == "CONVERB"
            and lemma == "ye"
            and suffix.startswith("y")
        ):
            old = stem
            stem = "yi"
            changes.append(f"LEXICAL_YE_YBUFFER:{old}->{stem}")

        subtype = None
        if feature == "CONVERB":
            # Construct a minimal virtual node only for subtype classification.
            subtype = (
                "IP" if suffix.endswith("p") else
                "ARAK" if suffix.endswith(("arak", "erek")) else
                "INCA" if suffix.endswith(("ınca", "ince", "unca", "ünce")) else
                None
            )
        if subtype:
            changes.append(f"CONVERB_SUBTYPE:{subtype}")

        return stem, tuple(changes)

    def _later_boundary_stem(
        self,
        current_surface: str,
        suffix: str,
        feature: str,
        previous_feature: Optional[str],
    ) -> Tuple[str, Tuple[str, ...]]:
        stem, changes = super()._later_boundary_stem(
            current_surface, suffix, feature, previous_feature
        )
        changes = list(changes)

        if feature == "CONVERB":
            # We only need previous_feature + suffix to recover subtype here.
            if suffix == "ken":
                subtype = "KEN"
            elif (
                suffix in {"dan", "den"}
                and previous_feature in {"NEGATION", "NEGATIVE_ABILITY"}
            ):
                subtype = "MADAN"
            elif suffix in {"ça", "çe"} and previous_feature == "PARTICIPLE_PAST":
                subtype = "DIKCA"
            elif suffix.endswith("p"):
                subtype = "IP"
            elif suffix.endswith(("arak", "erek")):
                subtype = "ARAK"
            elif suffix.endswith(("ınca", "ince", "unca", "ünce")):
                subtype = "INCA"
            else:
                subtype = None

            if subtype:
                changes.append(f"CONVERB_SUBTYPE:{subtype}")

        return stem, tuple(changes)

    def _transition_cost(
        self,
        feature: str,
        surface: str,
        root_known: bool,
    ) -> float:
        if feature == "CONVERB":
            return 0.14
        return super()._transition_cost(feature, surface, root_known)

    def analyze(self, word: str, n_best: int = 20) -> List[ParseResult]:
        results = super().analyze(word, n_best=max(80, n_best * 4))
        target = word.lower()
        clean = []

        for r in results:
            generated = None
            for note in reversed(r.notes):
                if note.startswith("generated="):
                    generated = note.split("=", 1)[1]
                    break

            # Exact finals carry surface_exact. Approximate COMPLETE lattice
            # nodes are never valid final analyses.
            if generated is not None and generated != target and "surface_exact" not in r.notes:
                continue
            clean.append(r)

        return clean[:n_best]


class TurkishMorphDisambiguatorV552(TurkishMorphDisambiguatorV55):
    """
    Same v5.5/v5.4 ranking. No P0-2 ranking heuristic is introduced.
    Only the parser candidate space changes.
    """
    def __init__(self, parser: Optional[TurkishMorphologyV552] = None):
        self.parser = parser or TurkishMorphologyV552()


class TurkishContextualDisambiguatorV552(TurkishContextualDisambiguatorV55):
    """
    Same frozen contextual ranking over the expanded P0-2 candidate lattice.
    """
    def __init__(
        self,
        parser: Optional[TurkishMorphologyV552] = None,
        beam_width: int = 96,
        candidates_per_token: int = 20,
    ):
        super().__init__(
            parser=parser or TurkishMorphologyV552(),
            beam_width=beam_width,
            candidates_per_token=candidates_per_token,
        )


# Compatibility aliases.
TurkishMorphologyV53 = TurkishMorphologyV552
TurkishMorphDisambiguatorV53 = TurkishContextualDisambiguatorV552
TurkishContextualDisambiguatorV541 = TurkishContextualDisambiguatorV552


# ===========================================================================
# v5.5 P0-3 — INFINITIVE + VERBAL_NOUN vertical slice
# ===========================================================================

class TurkishMorphologyV553(TurkishMorphologyV552):
    """
    P0-3 verbal nominal system.

    New active ontology:
      INFINITIVE  = -mAk
      VERBAL_NOUN = -mA / -(y)Iş

    UD Turkish uses Vnoun as a broader superclass. We deliberately do NOT
    relabel -DIK / -(y)AcAK in this slice because those forms overlap with the
    existing participle ontology and require a later ambiguity treatment.

    Realization subtype metadata:
      INFINITIVE_SUBTYPE:MAK
      VNOUN_SUBTYPE:MA
      VNOUN_SUBTYPE:IS
    """

    ALLOMORPHS = dict(TurkishMorphologyV552.ALLOMORPHS)
    ALLOMORPHS["INFINITIVE"] = ("mak", "mek")
    ALLOMORPHS["VERBAL_NOUN"] = (
        "ma", "me",
        "ış", "iş", "uş", "üş",
        "yış", "yiş", "yuş", "yüş",
    )
    FEATURE_ORDER = tuple(ALLOMORPHS.keys())

    # Conservative lexical expansion for real-corpus verb stems used across
    # productive paradigms. Unknown-root productivity remains enabled.
    KNOWN_ROOTS = set(TurkishMorphologyV552.KNOWN_ROOTS) | {
        "sür", "yarat", "ısıt", "tanış", "öde", "açıkla", "yaşa",
        "paylaş", "bit", "sığ", "dinle", "inan", "yürü", "kullan",
        "kazan", "çık", "boz", "üret", "ara", "bak",
    }

    def _harden_transitions(self):
        super()._harden_transitions()

        # Positive / derived verbal stems.
        for src in (MorphState.ROOT, MorphState.DERIVED_VERBAL):
            self.grammar.add(
                src, "INFINITIVE", MorphState.NONFINITE, 0.17,
                note="P0-3 -mAk infinitive"
            )
            self.grammar.add(
                src, "VERBAL_NOUN", MorphState.NONFINITE, 0.18,
                note="P0-3 -mA/-(y)Iş verbal noun"
            )

        # Polarity/modality can feed verbal nouns:
        # gel-me-mek, yap-abil-mek, yap-ama-mak,
        # gel-me-me, yap-abil-me...
        self.grammar.add(
            MorphState.FINITE_TAM, "INFINITIVE", MorphState.NONFINITE, 0.17,
            note="P0-3 polarity/modality -> infinitive"
        )
        self.grammar.add(
            MorphState.FINITE_TAM, "VERBAL_NOUN", MorphState.NONFINITE, 0.18,
            note="P0-3 polarity/modality -> verbal noun"
        )

    def _infinitive_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        if not node.surface:
            return ()
        return ("m" + self._harmonic_A(node.surface) + "k",)

    def _verbal_noun_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        if not node.surface:
            return ()

        a = self._harmonic_A(node.surface)
        i = self._harmonic_I(node.surface)

        # -mA never needs a buffer consonant.
        ma = "m" + a

        # -(y)Iş takes y after a vowel-final verbal stem.
        buffer = "y" if node.surface[-1] in VOWELS else ""
        ish = buffer + i + "ş"
        return (ma, ish)

    def _allowed_features(self, node: ForwardNodeV534) -> List[Transition]:
        transitions = list(super()._allowed_features(node))

        if node.features and node.features[-1] == "INFINITIVE":
            # Modern -mAk forms behave nominally but do not normally take
            # possessive/plural morphology; Turkish switches to -mA for those
            # paradigms. Keep only directly attested consonant-initial cases.
            allowed_case = {"LOCATIVE", "ABLATIVE", "COMITATIVE"}
            transitions = [
                t for t in transitions
                if (
                    t.feature in allowed_case
                    or t.feature == "COMPLETE"
                )
            ]

        if node.features and node.features[-1] == "VERBAL_NOUN":
            # Verbal nouns take nominal morphology, never finite PERSON_*.
            transitions = [
                t for t in transitions
                if not t.feature.startswith("PERSON_")
            ]

        return transitions

    def _surfaces_for(self, node: ForwardNodeV534, feature: str) -> Tuple[str, ...]:
        if feature == "INFINITIVE":
            return self._infinitive_surfaces(node)

        if feature == "VERBAL_NOUN":
            return self._verbal_noun_surfaces(node)

        # Restrict case after -mAk to attested productive forms in this slice:
        # -makta/-mekte, -maktan/-mekten, -makla/-mekle.
        if node.features and node.features[-1] == "INFINITIVE":
            if feature == "LOCATIVE":
                return ("te", "ta")
            if feature == "ABLATIVE":
                return ("ten", "tan")
            if feature == "COMITATIVE":
                return ("le", "la")

        return super()._surfaces_for(node, feature)

    def _first_boundary_stem(
        self,
        lemma: str,
        suffix: str,
        feature: str,
    ) -> Tuple[str, Tuple[str, ...]]:
        stem, changes = super()._first_boundary_stem(lemma, suffix, feature)
        changes = list(changes)

        if feature == "INFINITIVE":
            changes.append("INFINITIVE_SUBTYPE:MAK")

        elif feature == "VERBAL_NOUN":
            subtype = "MA" if suffix in {"ma", "me"} else "IS"
            changes.append(f"VNOUN_SUBTYPE:{subtype}")

            # ye + -(y)Iş -> yiyiş. This is lexical stem allomorphy, not a
            # general y-buffer rule.
            if lemma == "ye" and subtype == "IS" and suffix.startswith("y"):
                old = stem
                stem = "yi"
                changes.append(f"LEXICAL_YE_VNOUN:{old}->{stem}")

        return stem, tuple(changes)

    def _later_boundary_stem(
        self,
        current_surface: str,
        suffix: str,
        feature: str,
        previous_feature: Optional[str],
    ) -> Tuple[str, Tuple[str, ...]]:
        stem, changes = super()._later_boundary_stem(
            current_surface, suffix, feature, previous_feature
        )
        changes = list(changes)

        if feature == "INFINITIVE":
            changes.append("INFINITIVE_SUBTYPE:MAK")
        elif feature == "VERBAL_NOUN":
            subtype = "MA" if suffix in {"ma", "me"} else "IS"
            changes.append(f"VNOUN_SUBTYPE:{subtype}")

        return stem, tuple(changes)

    def _transition_cost(
        self,
        feature: str,
        surface: str,
        root_known: bool,
    ) -> float:
        # Keep legacy NOMINALIZER_MA competitive so the frozen internal
        # benchmark is not silently redefined. External semantic projection
        # treats NOMINALIZER_MA as a VERBAL_NOUN alias.
        if feature == "INFINITIVE":
            return 0.17
        if feature == "VERBAL_NOUN":
            return 0.18
        return super()._transition_cost(feature, surface, root_known)


class TurkishMorphDisambiguatorV553(TurkishMorphDisambiguatorV552):
    """
    Ranking frozen: identical structural/contextual rules.
    Only candidate morphology is expanded.
    """
    def __init__(self, parser: Optional[TurkishMorphologyV553] = None):
        self.parser = parser or TurkishMorphologyV553()


class TurkishContextualDisambiguatorV553(TurkishContextualDisambiguatorV552):
    """
    Ranking frozen: v5.4.1 context on the expanded P0-3 lattice.
    """
    def __init__(
        self,
        parser: Optional[TurkishMorphologyV553] = None,
        beam_width: int = 96,
        candidates_per_token: int = 20,
    ):
        super().__init__(
            parser=parser or TurkishMorphologyV553(),
            beam_width=beam_width,
            candidates_per_token=candidates_per_token,
        )


# Compatibility aliases.
TurkishMorphologyV53 = TurkishMorphologyV553
TurkishMorphDisambiguatorV53 = TurkishContextualDisambiguatorV553
TurkishContextualDisambiguatorV541 = TurkishContextualDisambiguatorV553


# ===========================================================================
# v5.5 P0-4 — MOOD vertical slice
# ===========================================================================

class TurkishMorphologyV554(TurkishMorphologyV553):
    """
    P0-4 mood system.

    Active ontology:
      CONDITIONAL    -sA
      NECESSITATIVE  -mAlI
      OPTATIVE       -(y)A
      IMPERATIVE     zero mood marker + imperative person paradigm

    Important:
      - -sA is formally ambiguous between conditional/desiderative semantics.
        This slice generates CONDITIONAL morphology but does not add a ranking
        preference that forces every -sA reading to conditional.
      - Imperative 2SG has a zero mood marker and zero person surface.
      - Ranking weights remain frozen; only the candidate grammar expands.
    """

    ALLOMORPHS = dict(TurkishMorphologyV553.ALLOMORPHS)
    ALLOMORPHS.update({
        "CONDITIONAL": ("sa", "se", "ysa", "yse"),
        "NECESSITATIVE": ("malı", "meli"),
        "OPTATIVE": ("a", "e", "ya", "ye"),
        "IMPERATIVE": ("",),
    })
    FEATURE_ORDER = tuple(ALLOMORPHS.keys())

    KNOWN_ROOTS = set(TurkishMorphologyV553.KNOWN_ROOTS) | {
        "kavra", "emzir", "bindir", "kapat", "kurtul", "doyur",
        "öğren", "söyle", "paylaş", "sar", "soy", "eğit",
        "iste", "otur", "dön", "kızdır",
    }

    MOOD_FEATURES = {
        "CONDITIONAL", "NECESSITATIVE", "OPTATIVE", "IMPERATIVE"
    }

    # Mood is a verbal category. These lexical roots are explicitly
    # non-verbal in the current lexicon/benchmark ontology and must not seed
    # finite mood candidates such as *ev+OPTATIVE -> eve.
    NONVERBAL_ROOTS = frozenset({
        "ev","kitap","çocuk","araba","baş","güzel","sorumlu","başarısız",
        "genç","köy","tuz","yağ","akıl","renk","ağaç","ağız","burun","omuz",
        "oğul","karın","şehir","fikir","zengin","dar","geniş","okul","masa",
        "bahçe","sınıf","arkadaş","kanat","çay","dil","hız",
    })

    def parse(self, word: str, max_nodes: int = 24000) -> MorphologicalLattice:
        # P0 expansion grows the valid lattice. Preserve pre-v5.5 oracle
        # coverage by raising the search budget rather than pruning old paths.
        return super().parse(word, max_nodes=max_nodes)

    def _harden_transitions(self):
        super()._harden_transitions()

        # Turkish mood material can follow a lexical/derived verb, polarity,
        # ability, and selected TAM layers. Surface rules below control which
        # realizations actually survive.
        for src in (
            MorphState.ROOT,
            MorphState.DERIVED_VERBAL,
            MorphState.FINITE_TAM,
        ):
            self.grammar.add(
                src, "CONDITIONAL", MorphState.FINITE_TAM, 0.13,
                note="P0-4 -sA conditional"
            )
            self.grammar.add(
                src, "NECESSITATIVE", MorphState.FINITE_TAM, 0.13,
                note="P0-4 -mAlI necessitative"
            )
            self.grammar.add(
                src, "OPTATIVE", MorphState.FINITE_TAM, 0.13,
                note="P0-4 -(y)A optative"
            )
            self.grammar.add(
                src, "IMPERATIVE", MorphState.FINITE_TAM, 0.12,
                note="P0-4 zero imperative mood"
            )

    def _mood_A(self, stem: str) -> str:
        return self._harmonic_A(stem)

    def _conditional_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        if not node.surface:
            return ()

        a = self._mood_A(node.surface)
        bare = "s" + a

        # After vowel-final PAST/NECESSITATIVE morphology Turkish inserts y:
        # geldi-y-se, gitmeli-y-se. Direct vowel-final lexical roots and
        # negative -mA take bare -sA: oku-sa, gelme-se.
        if (
            node.surface[-1] in VOWELS
            and node.features
            and node.features[-1] in {"PAST", "NECESSITATIVE"}
        ):
            return ("y" + bare,)
        return (bare,)

    def _necessitative_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        if not node.surface:
            return ()
        a = self._mood_A(node.surface)
        i = self._harmonic_I(node.surface + a)
        return ("m" + a + "l" + i,)

    def _optative_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        if not node.surface:
            return ()
        a = self._mood_A(node.surface)
        if node.surface[-1] in VOWELS:
            return ("y" + a,)
        return (a,)

    def _imperative_surfaces(self, node: ForwardNodeV534) -> Tuple[str, ...]:
        # Mood itself is zero; person morphology carries the overt paradigm.
        return ("",)

    def _person_surfaces_after_mood(
        self,
        node: ForwardNodeV534,
        feature: str,
    ) -> Optional[Tuple[str, ...]]:
        if not node.features:
            return None

        prev = node.features[-1]
        i = self._harmonic_I(node.surface)
        a = self._harmonic_A(node.surface)

        if prev == "CONDITIONAL":
            return {
                "PERSON_1SG": ("m",),
                "PERSON_2SG": ("n",),
                "PERSON_3SG": ("",),
                "PERSON_1PL": ("k",),
                "PERSON_2PL": (
                    "n" + i + "z",
                ),
                "PERSON_3PL": ("l" + a + "r",),
            }.get(feature)

        if prev == "NECESSITATIVE":
            return {
                "PERSON_1SG": ("y" + i + "m",),
                "PERSON_2SG": ("s" + i + "n",),
                "PERSON_3SG": ("",),
                "PERSON_1PL": ("y" + i + "z",),
                "PERSON_2PL": ("s" + i + "n" + i + "z",),
                "PERSON_3PL": ("l" + a + "r",),
            }.get(feature)

        if prev == "OPTATIVE":
            return {
                "PERSON_1SG": ("y" + i + "m",),
                "PERSON_2SG": ("s" + i + "n",),
                "PERSON_3SG": ("",),
                "PERSON_1PL": ("l" + i + "m",),
                "PERSON_2PL": ("s" + i + "n" + i + "z",),
                "PERSON_3PL": ("l" + a + "r",),
            }.get(feature)

        if prev == "IMPERATIVE":
            # Core imperative cells:
            # 2SG zero, 2PL -(y)In, 3SG -sIn, 3PL -sInlAr.
            if feature == "PERSON_2SG":
                return ("",)
            if feature == "PERSON_2PL":
                buf = "y" if node.surface and node.surface[-1] in VOWELS else ""
                short = buf + i + "n"
                long = short + i + "z"
                return (short, long)
            if feature == "PERSON_3SG":
                return ("s" + i + "n",)
            if feature == "PERSON_3PL":
                return ("s" + i + "n" + "l" + a + "r",)
            return ()

        return None

    def _allowed_features(self, node: ForwardNodeV534) -> List[Transition]:
        transitions = list(super()._allowed_features(node))

        if node.state == MorphState.ROOT and not node.features:
            # P0-4 mood attaches to lexically licensed verbal roots. Unknown
            # surface-prefix seeds remain productive for the older morphology,
            # but they do not fan out into four new finite mood families.
            # This prevents ontology expansion from starving valid old paths.
            if (
                node.lemma in self.NONVERBAL_ROOTS
                or node.lemma not in self.roots
            ):
                transitions = [
                    t for t in transitions
                    if t.feature not in self.MOOD_FEATURES
                ]

        if node.features:
            last = node.features[-1]

            # Mood is close to the right edge of the finite predicate.
            # Polarity/ability/nonfinite morphology precedes mood; allowing
            # NEGATION or VNOUN after OPTATIVE/CONDITIONAL created impossible
            # analyses and crowded out old candidates.
            if last == "CONDITIONAL":
                transitions = [
                    t for t in transitions
                    if t.feature.startswith("PERSON_")
                    or t.feature in {"PAST", "EVIDENTIAL"}
                ]

            elif last == "NECESSITATIVE":
                transitions = [
                    t for t in transitions
                    if t.feature.startswith("PERSON_")
                    or t.feature in {"PAST", "EVIDENTIAL"}
                ]

            elif last == "OPTATIVE":
                transitions = [
                    t for t in transitions
                    if t.feature.startswith("PERSON_")
                    or t.feature == "PAST"
                ]

            elif last == "IMPERATIVE":
                # Imperative has no 1st-person cells in this ontology.
                transitions = [
                    t for t in transitions
                    if t.feature in {
                        "PERSON_2SG", "PERSON_2PL",
                        "PERSON_3SG", "PERSON_3PL",
                    }
                ]

        return transitions

    def _surfaces_for(self, node: ForwardNodeV534, feature: str) -> Tuple[str, ...]:
        if feature == "CONDITIONAL":
            return self._conditional_surfaces(node)
        if feature == "NECESSITATIVE":
            return self._necessitative_surfaces(node)
        if feature == "OPTATIVE":
            return self._optative_surfaces(node)
        if feature == "IMPERATIVE":
            return self._imperative_surfaces(node)

        if feature.startswith("PERSON_"):
            specialized = self._person_surfaces_after_mood(node, feature)
            if specialized is not None:
                return specialized

        return super()._surfaces_for(node, feature)

    def _first_boundary_stem(
        self,
        lemma: str,
        suffix: str,
        feature: str,
    ) -> Tuple[str, Tuple[str, ...]]:
        stem, changes = super()._first_boundary_stem(lemma, suffix, feature)
        changes = list(changes)

        # Extend the lexical verbal t->d alternation to vowel-initial
        # P0-4/nonfinite environments. This is still lexical, not universal.
        if (
            feature in {"OPTATIVE", "PASSIVE", "VERBAL_NOUN"}
            and suffix
            and suffix[0] in VOWELS
            and lemma in self.VERBAL_T_D_VOICING_ROOTS
            and stem.endswith("t")
        ):
            old = stem
            stem = stem[:-1] + "d"
            changes.append(f"LEXICAL_VERBAL_T_TO_D:{old}->{stem}")

        # de-/ye- before y-initial optative:
        # de + ye + lim -> diyelim
        # ye + ye + lim -> yiyelim
        if feature == "OPTATIVE" and suffix.startswith("y"):
            if lemma == "de":
                old = stem
                stem = "di"
                changes.append(f"LEXICAL_DE_OPTATIVE:{old}->{stem}")
            elif lemma == "ye":
                old = stem
                stem = "yi"
                changes.append(f"LEXICAL_YE_OPTATIVE:{old}->{stem}")

        if feature in self.MOOD_FEATURES:
            changes.append(f"MOOD:{feature}")

        return stem, tuple(changes)

    def _later_boundary_stem(
        self,
        current_surface: str,
        suffix: str,
        feature: str,
        previous_feature: Optional[str],
    ) -> Tuple[str, Tuple[str, ...]]:
        stem, changes = super()._later_boundary_stem(
            current_surface, suffix, feature, previous_feature
        )
        changes = list(changes)

        # et/git + vowel-initial imperative 2PL:
        # et + Ø + in -> edin
        # git + Ø + in -> gidin
        if (
            previous_feature == "IMPERATIVE"
            and feature == "PERSON_2PL"
            and suffix
            and suffix[0] in VOWELS
            and current_surface in {"et", "git"}
        ):
            old = stem
            stem = stem[:-1] + "d"
            changes.append(f"LEXICAL_IMPERATIVE_T_TO_D:{old}->{stem}")

        # Vowel-final mood + past/evidential takes buffer y:
        # gitmeli + di -> gitmeliydi
        # gelse + ydi   -> gelseydi
        if (
            previous_feature in {"NECESSITATIVE", "CONDITIONAL"}
            and feature in {"PAST", "EVIDENTIAL"}
            and suffix
            and stem
            and stem[-1] in VOWELS
        ):
            old = stem
            stem = stem + "y"
            changes.append(f"MOOD_BUFFER_Y:{old}->{stem}")

        if feature in self.MOOD_FEATURES:
            changes.append(f"MOOD:{feature}")

        return stem, tuple(changes)

    def _transition_cost(
        self,
        feature: str,
        surface: str,
        root_known: bool,
    ) -> float:
        if feature in self.MOOD_FEATURES:
            return 0.13
        return super()._transition_cost(feature, surface, root_known)

    def _zero_imperative_candidates(
        self,
        word: str,
        existing: List[ParseResult],
    ) -> List[ParseResult]:
        """
        Parser nodes that already equal the target normally stop expanding.
        Therefore bare 2SG imperatives (gel!, yap!) and negative 2SG forms
        (gelme!, yapma!) need explicit zero-morph candidates.
        """
        target = word.lower()
        out = []

        # Positive bare imperative.
        if target in self.roots:
            out.append(ParseResult(
                lemma=target,
                features=("IMPERATIVE", "PERSON_2SG"),
                realizations=(
                    Realization("IMPERATIVE", "", ("MOOD:IMPERATIVE",)),
                    Realization("PERSON_2SG", "", ("IMPERATIVE_ZERO_2SG",)),
                ),
                state=MorphState.COMPLETE,
                score=0.17,
                complete=True,
                notes=("ZERO_IMPERATIVE_2SG", "surface_exact", f"generated={target}"),
            ))

        # Negative bare imperative: root + -mA.
        for root in self.roots:
            if len(root) < 2:
                continue
            a = self._harmonic_A(root)
            neg = root + "m" + a
            if target == neg:
                out.append(ParseResult(
                    lemma=root,
                    features=("NEGATION", "IMPERATIVE", "PERSON_2SG"),
                    realizations=(
                        Realization("NEGATION", "m" + a),
                        Realization("IMPERATIVE", "", ("MOOD:IMPERATIVE",)),
                        Realization("PERSON_2SG", "", ("IMPERATIVE_ZERO_2SG",)),
                    ),
                    state=MorphState.COMPLETE,
                    score=0.31,
                    complete=True,
                    notes=("ZERO_NEGATIVE_IMPERATIVE_2SG", "surface_exact", f"generated={target}"),
                ))

        return out

    def analyze(self, word: str, n_best: int = 20) -> List[ParseResult]:
        # Expanded ontology requires a broader pre-ranking candidate pool.
        results = list(super().analyze(word, n_best=max(100, n_best * 5)))
        results.extend(self._zero_imperative_candidates(word, results))

        # Deduplicate exact structural signatures, retaining the lowest score.
        best = {}
        for r in results:
            sig = (
                r.lemma,
                tuple(r.features),
                tuple((x.morph, x.surface, tuple(x.changes)) for x in r.realizations),
            )
            old = best.get(sig)
            if old is None or r.score < old.score:
                best[sig] = r

        return sorted(
            best.values(),
            key=lambda r: (r.score, -len(r.features), r.lemma),
        )[:n_best]


class TurkishMorphDisambiguatorV554(TurkishMorphDisambiguatorV553):
    """
    Structural ranking rules are frozen. The only update is recognizing the
    new mood labels as finite domains, so PERSON_* is not falsely penalized.
    """
    FINITE_TAM = set(TurkishMorphDisambiguatorV553.FINITE_TAM) | {
        "CONDITIONAL", "NECESSITATIVE", "OPTATIVE", "IMPERATIVE"
    }

    def __init__(self, parser: Optional[TurkishMorphologyV554] = None):
        self.parser = parser or TurkishMorphologyV554()

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        pool = max(240, n_best * 12)
        candidates = self.parser.analyze(word, n_best=pool)
        ranked = sorted(
            enumerate(candidates),
            key=lambda item: (
                self._decision(word, item[1]).total_score,
                item[0],
            ),
        )
        return [cand for _, cand in ranked][:n_best]


class TurkishContextualDisambiguatorV554(TurkishContextualDisambiguatorV553):
    """
    Context scoring remains frozen; only finite-domain recognition expands.
    """
    FINITE_TAM = set(TurkishContextualDisambiguatorV553.FINITE_TAM) | {
        "CONDITIONAL", "NECESSITATIVE", "OPTATIVE", "IMPERATIVE"
    }

    def __init__(
        self,
        parser: Optional[TurkishMorphologyV554] = None,
        beam_width: int = 96,
        candidates_per_token: int = 20,
    ):
        super().__init__(
            parser=parser or TurkishMorphologyV554(),
            beam_width=beam_width,
            candidates_per_token=candidates_per_token,
        )

    def analyze_word(self, word: str, n_best: int = 20) -> List[ParseResult]:
        pool = max(240, n_best * 12)
        candidates = self.parser.analyze(word, n_best=pool)
        ranked = sorted(
            enumerate(candidates),
            key=lambda item: (
                self._decision(word, item[1]).total_score,
                item[0],
            ),
        )
        return [cand for _, cand in ranked][:n_best]

    def _raw_candidates(self, word: str) -> List[ParseResult]:
        return self.parser.analyze(
            word, n_best=max(240, self.candidates_per_token * 12)
        )


TurkishMorphologyV53 = TurkishMorphologyV554
TurkishMorphDisambiguatorV53 = TurkishContextualDisambiguatorV554
TurkishContextualDisambiguatorV541 = TurkishContextualDisambiguatorV554
