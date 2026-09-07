"""Usable local API and CLI for the S02 development version."""
import argparse
import copy
import json
import re
from pathlib import Path
import bootstrap
from bootstrap import ROOT, UPSTREAM
from common import Runtime, lower
from r5.conditions import check_record
from r5.engine import fingerprint
from r5.lexicon import last_vowel
from analyzer_s02 import S02Analyzer
from context_s02 import S02Selector
from segmentation_s02 import spans
from numerals_s02 import integer_words, final_reading

def read(path):
    return Path(path).read_text(encoding="utf-8")

class S02Runtime(Runtime):
    def __init__(self, analyzer=None, context_enabled=True, context_mode="hybrid", context_model=None):
        super().__init__(analyzer or S02Analyzer(), context_enabled, context_mode)
        self.abbreviations = {}
        for line in read(UPSTREAM / "base/data/abbreviations.dict").splitlines():
            if line.startswith("##") or " [" not in line:
                continue
            head, metadata = line.split(" [", 1)
            fields = dict(re.findall(r"(\w+):([^;\]]+)", metadata))
            # Explicit source references, not every corpus fragment in the list.
            if "Ref" in fields:
                self.abbreviations[head] = fields["Ref"].strip()
        if context_enabled and context_mode == "hybrid":
            self.context_selector = S02Selector(
                json.loads(read(UPSTREAM / "models/view-counts.json")), self.analyzer.rows,
                context_model if context_model is not None else json.loads(read(ROOT / "models/context-ranker.json")))

    def _atom(self, raw, lemma, pos, features, kind):
        normalized = lower(raw).replace("’", "'")
        surface = normalized.replace("'", "")
        aid = fingerprint(["S02_ORTHOGRAPHIC", normalized, lemma, pos, features])[:24]
        candidate = {"lexeme_id": "S02:" + kind + ":" + lemma, "lemma": lemma,
                     "root_pos": pos, "output_pos": pos, "record_ids": [], "morpheme_ids": [],
                     "features": features, "surface": surface, "realization_trace": [],
                     "registry_version": self.analyzer.version, "source": "S02_ORTHOGRAPHIC_ATOM",
                     "cost": 0., "analysis_id": aid, "derivation_key": aid,
                     "orthographic_kind": kind, "semantic_interpretation": "NOT_INFERRED"}
        return {"raw": raw, "normalized": normalized, "status": "ANALYZED",
                "search_complete": True, "analyses": [candidate],
                "ranking": "ORTHOGRAPHIC_CLASS", "manifest": self.analyzer.manifest()}

    def analyze_orthographic(self, raw, kind):
        if kind in {"URL", "EMAIL", "IDENTIFIER"}:
            return self._atom(raw, lower(raw), "X", {}, kind)
        if kind == "NUMBER" and not any(c in raw for c in "'’"):
            return self._atom(raw, raw, "NUM", {}, kind)
        if kind == "ORDINAL":
            lemma = integer_words(raw[:-1])
            if lemma:
                return self._atom(raw, lemma, "NUM", {"NumType": "Ord"}, kind)
        if kind == "NUMBER" and any(c in raw for c in "'’"):
            return self._inflected_number(raw)
        if kind == "ABBREVIATION" and raw[:-1] in self.abbreviations:
            lemma = lower(self.abbreviations[raw[:-1]])
            lexemes = self.analyzer.lexicon.by_stem.get(lemma, [])
            if len({entry.pos for entry in lexemes}) == 1:
                return self._atom(raw, lemma, lexemes[0].pos, {}, kind)
        return Runtime.analyze_word(self, raw)

    def _inflected_number(self, raw):
        base, suffix = re.split("['’]", lower(raw), maxsplit=1)
        reading = final_reading(base)
        result = Runtime.analyze_word(self, raw)
        if not reading:
            return result
        phonetic_stems = {reading}
        for lexeme in self.analyzer.lexicon.by_stem.get(reading, []):
            if lexeme.pos == "NUM":
                phonetic_stems.update(self.analyzer.lexicon.seed_variants(lexeme))
        native_results = [self.analyzer.analyze(stem + suffix) for stem in sorted(phonetic_stems)]
        native_analyses = {a["analysis_id"]: a for result in native_results for a in result["analyses"]}
        candidates = []
        for original in native_analyses.values():
            # Interpret the written number using an actual cardinal lexeme and
            # the registry's vowel-harmony/voicing constraints. Do not accept
            # homographic nouns/verbs or derive new words from a digit string.
            if original["root_pos"] != "NUM" or original["lemma"] != reading:
                continue
            if not original["morpheme_ids"] or not all(mid.startswith(("CASE_", "POSS_", "NUMBER_")) for mid in original["morpheme_ids"]):
                continue
            a = copy.deepcopy(original)
            for trace in a["realization_trace"]:
                for key in ("before", "realized_stem", "after"):
                    trace[key] = base + trace[key][len(reading):]
            a.update(lemma=base, root_pos="NUM", output_pos="NUM", surface=base + suffix,
                     lexeme_id="S02:NUM:" + base, source="S02_NUMERAL_WITH_REGISTRY_SUFFIX",
                     phonetic_lemma=reading, native_analysis_id=original["analysis_id"])
            a["analysis_id"] = fingerprint(["S02_NUMERAL", raw, original["analysis_id"]])[:24]
            a["derivation_key"] = fingerprint([base, a["output_pos"], a["morpheme_ids"], a["features"]])[:24]
            candidates.append(a)
        return {**result, "status": "ANALYZED" if candidates else "UNRESOLVED",
                "analyses": candidates, "search_complete": all(r["search_complete"] for r in native_results),
                "numeric_reading": reading, "ranking": "STRUCTURAL_COST_NOT_CONTEXTUAL_PROBABILITY"}

    def analyze_word(self, word, n_best=None):
        parts = list(spans(word, self.abbreviations))
        if len(parts) == 1 and parts[0].start == 0 and parts[0].end == len(word):
            result = self.analyze_orthographic(word, parts[0].kind)
        else:
            result = Runtime.analyze_word(self, word)
        if n_best is None:
            return result
        if not isinstance(n_best, int) or n_best < 0:
            raise ValueError("n_best must be a nonnegative integer")
        return {**result, "analyses": result["analyses"][:n_best],
                "selection_truncated": len(result["analyses"]) > n_best}

    def analyze_sentence(self, text):
        tokens = []
        cursor = 0
        for span in spans(text, self.abbreviations):
            raw = text[span.start:span.end]
            result = self.analyze_orthographic(raw, span.kind)
            boundaries = []
            if tokens:
                host = tokens[-1]["raw"]
                for record in self.analyzer.rows.values():
                    if record["class_tag"] not in {"soK", "odK", "bgK", "isK"} or record["surface"] != lower(raw):
                        continue
                    ctx = {"pos": "CLAUSE" if record["class_tag"] == "bgK" else "HOST",
                           "last_vowel": last_vowel(host), "last_voiceless": lower(host)[-1] in "fstkçşhp"}
                    if check_record(record, ctx)["accepted"]:
                        boundaries.append({"record_id": record["id"], "morpheme_ids": record["morpheme_ids"],
                                           "surface_host_index": len(tokens) - 1, "scope_status": "UNRESOLVED",
                                           "status": "ORTHOGRAPHIC_AND_LOCAL_HARMONY_CANDIDATE"})
            tokens.append({"raw": raw, "start": span.start, "end": span.end,
                           "leading": text[cursor:span.start], "orthographic_kind": span.kind,
                           "boundary_candidates": boundaries, "analysis": result,
                           "selection_status": "UNRESOLVED" if len(result["analyses"]) != 1 else "SINGLE_GRAMMAR_CANDIDATE"})
            cursor = span.end
        sentence = {"raw": text, "tokens": tokens, "trailing": text[cursor:],
                    "manifest": self.analyzer.manifest(), "context_model": "NOT_TRAINED",
                    "discourse_status": "NOT_RESOLVED", "tokenizer_version": "S02-v0.1.0"}
        return self.context_selector.apply(sentence) if self.context_selector else sentence

def main():
    parser = argparse.ArgumentParser(description="TürkTokenizer S02: yerel bağlam ve sözcük çözümlemesi")
    parser.add_argument("text", nargs="?")
    parser.add_argument("--file", type=Path, help="UTF-8 metin dosyası")
    parser.add_argument("--output", type=Path, help="Ayrıntılı JSON çıktısı")
    parser.add_argument("--no-context", action="store_true")
    parser.add_argument("--context-model", choices=("s01", "ensemble", "residual"), default="s01",
                        help="Bağlam puan modeli; varsayılan s01, diğerleri S02 deneyleridir")
    args = parser.parse_args()
    if bool(args.text is not None) == bool(args.file):
        parser.error("Metin veya --file seçeneklerinden tam birini verin.")
    model_path = {"s01": "context-ranker.json", "ensemble": "context-ensemble-s02.json", "residual": "context-residual-s02.json"}[args.context_model]
    model = json.loads(read(ROOT / "models" / model_path)) if not args.no_context else None
    out = S02Runtime(context_enabled=not args.no_context, context_model=model).analyze_sentence(read(args.file) if args.file else args.text)
    encoded = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")

if __name__ == "__main__":
    main()
