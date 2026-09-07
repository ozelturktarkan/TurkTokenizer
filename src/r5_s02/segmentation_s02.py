"""Lossless orthographic tokenization; offsets always refer to the original text."""
import re
import unicodedata
from dataclasses import dataclass

URL = re.compile(r"(?:https?://|www\.)[^\s<>\"“”]+", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.UNICODE)
NUMBER = re.compile(r"%?\d+(?:[.,:/]\d+)*(?:['’][^\W\d_]+)?", re.UNICODE)
INITIALS = re.compile(r"(?:[A-ZÇĞİÖŞÜ]\.){2,}(?:['’][^\W\d_]+)?")
APOSTROPHES = "'’"

@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str

def word_character(c):
    return c == "_" or unicodedata.category(c)[0] in "LNM"

def spans(text, abbreviations=frozenset()):
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        start = i
        match = URL.match(text, i)
        if match:
            end = match.end()
            while end > i and text[end - 1] in ".,;:!?":
                end -= 1
            for left, right in (("(", ")"), ("[", "]"), ("{", "}")):
                while text[i:end].endswith(right) and text[i:end].count(right) > text[i:end].count(left):
                    end -= 1
            yield Span(i, end, "URL")
            i = end
            continue
        for pattern, kind in ((EMAIL, "EMAIL"), (INITIALS, "ABBREVIATION"), (NUMBER, "NUMBER")):
            match = pattern.match(text, i)
            if not match:
                continue
            end = match.end()
            # An identifier such as 12abc is one token, not a number plus a word.
            if kind == "NUMBER" and end < len(text) and word_character(text[end]):
                continue
            if kind == "NUMBER" and text[i:end].isdigit() and text[end:end + 1] == ".":
                following = text[end + 1:].lstrip()
                # The period is ambiguous at sentence end; preserve it there.
                if following[:1].islower():
                    end += 1
                    kind = "ORDINAL"
            yield Span(i, end, kind)
            i = end
            break
        if i != start:
            continue
        if word_character(text[i]):
            i += 1
            while i < len(text):
                if word_character(text[i]):
                    i += 1
                elif text[i] in APOSTROPHES and i + 1 < len(text) and word_character(text[i + 1]):
                    i += 1
                elif (text[i] in "-‐‑" and i + 1 < len(text)
                      and text[start:start + 1].isupper() and text[i + 1:i + 2].isupper()):
                    # Paired named terms (Türkçe-İngilizce). A bare hyphen is
                    # also used for parenthetical clauses; never merge every
                    # adjacent word merely because spaces were omitted.
                    i += 1
                else:
                    break
            raw = text[start:i]
            kind = "IDENTIFIER" if "_" in raw else "HYPHENATED" if any(c in raw for c in "-‐‑") else "WORD"
            if text[i:i + 1] == "." and raw in abbreviations:
                i += 1
                kind = "ABBREVIATION"
            yield Span(start, i, kind)
        else:
            i += 1
            yield Span(start, i, "PUNCTUATION")
