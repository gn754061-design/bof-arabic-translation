# -*- coding: utf-8 -*-
"""
Arabic shaping + visual-order conversion + BoF GBA encoding.

Encoding (from ROM charmap):
  0x00 END, 0x03 newline, 0x04 COLOR, 0x05 PLAYER, 0x06 NAME(+1),
  0x09 NEW(page), 0x0A STRING, 0x0B ITEM, 0x0C WEAPON, 0x0D DEFENSE
  0x02 space, 0x20-0x29 digits, 0x45 '!', 0x46 '?', 0x62 '\'', 0x63 ',',
  0x64 ':', 0x67 '&', 0x68 ';', 0xEF '.', 0xF0 '-', 0xF7 '...'
Arabic letter forms are mapped onto codes 0x80-0xE8 by arabic_codes.json.
"""
import json, re, unicodedata

CODES = json.load(open(r"C:\Users\reva4\Desktop\game\font\arabic_codes.json", encoding="utf-8"))
# CODES: "80" -> [letter, form]

# build encode maps: (letter, form) -> code ; letter -> iso code
FORM_CODE = {}
ISO_CODE = {}
LIG_CODE = {}
for k, (letter, frm) in CODES.items():
    c = int(k, 16)
    FORM_CODE[(letter, frm)] = c
    if frm == "ISO" and letter not in LIG_CODE:
        ISO_CODE.setdefault(letter, c)
    if frm == "LIG":
        LIG_CODE[letter] = c

DUAL = set(l for (l, f) in FORM_CODE if f == "MEDI")
NONCONN = set(l for l in ISO_CODE if l not in DUAL)

# basic mappings for punctuation / symbols (logical char -> game code)
BASIC = {
    " ": 0x02, "0": 0x20, "1": 0x21, "2": 0x22, "3": 0x23, "4": 0x24,
    "5": 0x25, "6": 0x26, "7": 0x27, "8": 0x28, "9": 0x29,
    "!": 0x45, "?": 0x46, "'": 0x62, ",": 0x63, ":": 0x64, "&": 0x67,
    ";": 0x68, ".": 0xEF, "-": 0xF0, "…": 0xF7, "\u00b7": 0xF7,
    "\u060c": 0x63,   # arabic comma
    "\u061b": 0x68,   # arabic semicolon
    "\u061f": 0x46,   # arabic question mark
    "\u066d": 0x2A,   # arabic five pointed star -> '*'? map below
}

# normalize input: strip tashkeel (harakat) - the font has no diacritics
TASHKEEL = re.compile("[\u064b-\u0652\u0670\u0640]")

ARABIC_LETTER = re.compile(r"[\u0621-\u064a\u0671-\u06d3]")
ALEFS = "اأإآ"
LIGS = {"لا": "لا", "لأ": "لأ", "لإ": "لإ", "لآ": "لآ"}

def shape_arabic(text):
    """Return list of form-codes for an Arabic run (logical order)."""
    words = re.split(r"(\s+)", text)
    out = []
    for w in words:
        if not w or w.isspace():
            continue
        letters = list(w)
        n = len(letters)
        i = 0
        while i < n:
            L = letters[i]
            # lam-alef ligature
            if L == "ل" and i + 1 < n and letters[i + 1] in ALEFS:
                lig = LIGS.get(L + letters[i + 1])
                if lig and lig in LIG_CODE:
                    out.append(LIG_CODE[lig])
                    i += 2
                    continue
            prev_joins = i > 0 and (letters[i - 1] in DUAL or
                                    (letters[i - 1] == "ل" and L in ALEFS))
            next_joins = i < n - 1 and letters[i + 1] in DUAL
            if L in DUAL:
                if prev_joins and next_joins:
                    frm = "MEDI"
                elif prev_joins:
                    frm = "FIN"
                elif next_joins:
                    frm = "INIT"
                else:
                    frm = "ISO"
            elif L in NONCONN:
                frm = "ISO"
            else:
                i += 1
                continue
            out.append(FORM_CODE[(L, frm)])
            i += 1
    return out

def to_visual(text):
    """Convert Arabic text (logical order, mixed with digits/punct) to game codes
    in visual order with contextual shaping applied."""
    # tokenize into arabic runs and other runs
    tokens = []
    buf = ""
    mode = None
    for ch in text:
        if ARABIC_LETTER.match(ch):
            m = "ar"
        elif ch.isdigit() or ch in "!?:,.'-&\";()%":
            m = "other"
        else:
            m = "other"
        if mode is None:
            mode, buf = m, ch
        elif m == mode:
            buf += ch
        else:
            tokens.append((mode, buf))
            mode, buf = m, ch
    if buf:
        tokens.append((mode, buf))

    # shape each arabic token, reverse arabic tokens (visual order)
    encoded_tokens = []
    for m, t in tokens:
        if m == "ar":
            encoded_tokens.append(("ar", shape_arabic(t)))
        else:
            # keep latin/digit runs in logical order
            codes = []
            for ch in t:
                if ch in BASIC:
                    codes.append(BASIC[ch])
            if codes:
                encoded_tokens.append(("other", codes))
    # reverse token order (visual), arabic token content is already reversed
    # because shaping produced logical order -> we reverse the letter sequence
    visual = []
    for m, codes in reversed(encoded_tokens):
        if m == "ar":
            visual.extend(reversed(codes))
        else:
            visual.extend(codes)
    return visual

def encode_marked(marked):
    """Encode a translation template that contains {TOKEN} placeholders.
    Arabic runs are shaped and stored in visual order; tokens stay in place
    as {NAME} strings for the caller to turn into control bytes."""
    out = []
    parts = re.split(r"(\{[A-Z0-9]+\})", marked)
    for p in parts:
        if not p:
            continue
        if re.fullmatch(r"\{[A-Z0-9]+\}", p):
            out.append(p)
        else:
            out.extend(to_visual(p))
    return out

if __name__ == "__main__":
    tests = ["استفق أيها المحارب!", "المدرسة", "قلعة التنين", " genie 3"]
    for t in tests:
        codes = to_visual(t)
        print(t, "->", " ".join("%02X" % c for c in codes))
