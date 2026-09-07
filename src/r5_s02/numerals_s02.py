"""Turkish numeral readings for validating apostrophe suffixes via native grammar.

Only the final spoken cardinal is needed for vowel harmony. Decimal and clock
tails use the final component. Grouped thousands are recognized separately.
No evaluation labels or precomputed surface answers are consumed.
"""
import re

ONES = ("sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
TENS = ("", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan")
SCALES = ("", "bin", "milyon", "milyar", "trilyon", "katrilyon")

def integer_words(digits):
    if not digits.isascii() or not digits.isdigit() or len(digits) > 18:
        return None
    value = int(digits)
    if not value:
        return "sıfır"
    groups = []
    scale = 0
    while value:
        value, group = divmod(value, 1000)
        if group:
            parts = []
            hundreds, remainder = divmod(group, 100)
            if hundreds:
                if hundreds != 1:
                    parts.append(ONES[hundreds])
                parts.append("yüz")
            tens, ones = divmod(remainder, 10)
            if tens:
                parts.append(TENS[tens])
            if ones:
                parts.append(ONES[ones])
            if scale == 1 and group == 1:
                parts = []
            if scale:
                parts.append(SCALES[scale])
            groups.append(" ".join(parts))
        scale += 1
    return " ".join(reversed(groups))

def final_reading(base):
    base = base.removeprefix("%")
    if re.fullmatch(r"[1-9]\d{0,2}(?:\.\d{3})+", base):
        number = base.replace(".", "")
    else:
        number = re.split(r"[.,:/]", base)[-1]
    words = integer_words(number)
    return words.split()[-1] if words else None
