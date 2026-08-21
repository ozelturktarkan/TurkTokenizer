#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lossless runtime token layer for TurkTokenizer v5.11-v4.

Design constraints
------------------
* Preserve the raw span seen in the input text.
* Expose a normalized ``analysis`` surface to the frozen v5.5.4 morphology.
* Keep punctuation as hard/soft boundary metadata rather than encoder tokens.
* Preserve Unicode letters, digits, apostrophe suffixes, numeric ranges,
  clock-time colons, meta-prefixes (>), symbol-prefixes (°), and standalone
  semantic symbols used as syntactic tokens by the locked training corpora.

This module does NOT modify morphology or relation scores.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Iterator, Tuple

APOS = {"'", "’"}
HARD = set(".!?;:")
SOFT = {",", "–", "—"}
PREFIX_SYMBOLS = {">", "°"}
STANDALONE_SYMBOLS = {"%", "‰", "₺", "$", "€", "£", "¥", "+", "="}

@dataclass(frozen=True)
class RuntimeTokenV511:
    raw: str
    analysis: str
    start: int
    end: int
    kind: str
    hard_boundary_after: bool = False
    soft_boundary_after: bool = False


def _is_letter(ch: str) -> bool:
    return bool(ch) and unicodedata.category(ch).startswith("L")


def _is_mark(ch: str) -> bool:
    return bool(ch) and unicodedata.category(ch).startswith("M")


def _is_alnum_core(ch: str) -> bool:
    return bool(ch) and (ch.isdigit() or _is_letter(ch) or _is_mark(ch))


def _classify(core: str, prefix: str = "") -> str:
    z = core.replace("'", "").replace("’", "")
    if prefix == ">":
        return "META_WORD"
    if prefix == "°" or prefix in STANDALONE_SYMBOLS:
        return "SYMBOL_WORD"
    if "-" in z:
        parts = z.split("-")
        if parts and all(p.replace(".", "", 1).replace(",", "", 1).isdigit() for p in parts if p):
            return "NUMERIC_RANGE"
    has_d = any(c.isdigit() for c in z)
    has_l = any(_is_letter(c) for c in z)
    if has_d and has_l:
        return "ALPHANUMERIC"
    if has_d and not has_l:
        return "NUMERIC"
    return "WORD"


def _analysis_surface(raw: str) -> str:
    z = raw.replace("’", "'")
    # Meta/symbol prefixes are informative raw-span material but are not
    # morphology characters in the frozen analyzer.
    while z.startswith(tuple(PREFIX_SYMBOLS)):
        z = z[1:]
    # Terminal period is retained in raw span (abbreviations, ordinals,
    # sentence-final lexical tokens) but supplied as boundary metadata.
    if z.endswith(".") and len(z) > 1:
        z = z[:-1]
    return z


def _scan_token(text: str, i: int) -> Tuple[int, str] | None:
    n = len(text)
    start = i
    prefix = ""
    if text[i] in STANDALONE_SYMBOLS:
        return i + 1, text[i]
    if text[i] in PREFIX_SYMBOLS:
        if i + 1 >= n or not _is_alnum_core(text[i + 1]):
            return None
        prefix = text[i]
        i += 1
    if i >= n or not _is_alnum_core(text[i]):
        return None

    j = i
    saw_digit = False
    while j < n:
        c = text[j]
        if _is_alnum_core(c):
            saw_digit |= c.isdigit()
            j += 1
            continue
        if c in APOS:
            # Apostrophe belongs to the token only when followed by a core
            # character; this covers Turkish proper-noun and numeral suffixes.
            if j + 1 < n and _is_alnum_core(text[j + 1]):
                j += 1
                continue
            break
        if c == "-":
            # Preserve numeric ranges and genuine hyphenated alnum forms, but
            # never absorb punctuation dashes without a right-hand token.
            if j > i and j + 1 < n and _is_alnum_core(text[j + 1]):
                j += 1
                continue
            break
        if c in {".", ",", ":"}:
            # Decimal/thousands punctuation is internal only when surrounded
            # by digits. A terminal period may still be captured below.
            if j > i and j + 1 < n and text[j - 1].isdigit() and text[j + 1].isdigit():
                j += 1
                continue
            break
        break

    # Retain one terminal period in raw span. It is simultaneously exposed as
    # a hard boundary. This supports St., 19., and corpus lexical-period forms
    # without leaking the period into frozen morphology.
    if j < n and text[j] == ".":
        j += 1

    return j, prefix


def tokenize_runtime_v511(text: str) -> Tuple[RuntimeTokenV511, ...]:
    """Return lossless content-token spans with boundary metadata."""
    spans = []
    i = 0
    n = len(text)
    while i < n:
        got = _scan_token(text, i)
        if got is None:
            i += 1
            continue
        j, prefix = got
        raw = text[i:j]
        analysis = _analysis_surface(raw)
        if not analysis:
            i = max(j, i + 1)
            continue
        spans.append([i, j, raw, analysis, _classify(raw[len(prefix):], prefix)])
        i = j

    out = []
    for k, (s, e, raw, analysis, kind) in enumerate(spans):
        next_s = spans[k + 1][0] if k + 1 < len(spans) else n
        sep = text[e:next_s]
        # A terminal period can be part of raw for reconstruction while still
        # acting as a hard boundary.
        hard = raw.endswith(".") or any(c in HARD for c in sep)
        soft = any(c in SOFT for c in sep)
        out.append(RuntimeTokenV511(
            raw=raw,
            analysis=analysis,
            start=s,
            end=e,
            kind=kind,
            hard_boundary_after=hard,
            soft_boundary_after=soft,
        ))
    return tuple(out)


def semantic_surface(s: str) -> str:
    """Normalization used only for corpus/runtime alignment audits."""
    z=(unicodedata.normalize("NFKC",s or "").replace("’", "'")
       .replace("İ","i").replace("I","ı").casefold())
    if len(z) > 1 and z[0] == z[-1] and z[0] in {"'", '"'}:
        z=z[1:-1]
    while len(z)>1 and z[-1] in ".?!":
        z=z[:-1]
    return z


if __name__ == "__main__":
    import sys
    s = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "19. Molière'den 300-600 °C'de >kıral"
    for t in tokenize_runtime_v511(s):
        print(t)
