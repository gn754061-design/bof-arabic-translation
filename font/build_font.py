# -*- coding: utf-8 -*-
"""Build Arabic font tiles and inject them into the BoF (USA) GBA ROM."""
import os, sys, json

sys.path.insert(0, os.path.dirname(__file__))
from arabic_art import MEDIAL, NONCONN_ART, DUAL, NONCONN, art

ROM = os.environ.get("BOF_ROM", r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba")
OUT_ROM = os.environ.get("BOF_OUT", r"C:\Users\reva4\Desktop\game\build\bof_arabic.gba")

SMALL_BASE = 0x22FA68      # 8x8 glyphs, 32 bytes each (descriptor @0x14bb34)
LARGE_BASE = 0x231668      # 8x16 glyphs: top tile + (0x1C00) bottom tile
LARGE_BOT = LARGE_BASE + 0x1C00
BOLD_BASE = 0x23B668       # 8x16 bold font (descriptor @0x14bb94)
BOLD_BOT = BOLD_BASE + 0x1C00
# 8x8 special-purpose fonts (menu numbers/symbols) from the descriptor table:
#   base -> byte size (only the main small font can hold the Arabic range)
SMALL_FONTS = [
    (0x22FA68, 0x1C00),   # main small font (8x8)
    (0x23AE68, 0x200),
    (0x23B268, 0x200),
    (0x23EE68, 0x800),
    (0x23F668, 0x400),
    (0x23FA68, 0x800),
]

# ------------------------------------------------------------------ stubs ---
def add_stub(g, side):
    """side: 'R' = entry stub from previous letter (right edge, x=7)
             'L' = exit stub to next letter (left edge, x=0)"""
    rows = [list(r) for r in g]
    if side == "R":
        for y in (10, 11, 12):
            for x in (7, 6):
                if y < 16:
                    rows[y][x] = "#"
    else:
        for y in (10, 11, 12):
            for x in (0, 1):
                rows[y][x] = "#"
    return ["".join(r) for r in rows]

def form(g, which):
    if which == "ISO":
        return g
    if which == "FIN":
        return add_stub(g, "R")
    if which == "INIT":
        return add_stub(g, "L")
    if which == "MEDI":
        return add_stub(add_stub(g, "L"), "R")
    raise ValueError(which)

# -------------------------------------------------------------- code table --
def build_code_table():
    """Returns dict code -> (letter, form) and the glyph arts per code."""
    codes = {}
    art_by_code = {}
    c = 0x80
    for L in DUAL:
        for f in ("ISO", "INIT", "MEDI", "FIN"):
            codes[c] = (L, f)
            art_by_code[c] = form(MEDIAL[L], f)
            c += 1
    for L in NONCONN:
        codes[c] = (L, "ISO")
        art_by_code[c] = NONCONN_ART[L]
        c += 1
    # lam-alef ligatures
    LIG = {
        "لا": (7, 3),   # (x of alef bar, stub x) - drawn manually below
    }
    # لا / لأ / لإ / لآ : lam tail going right-up + alef bar
    arts = {}
    def lam_alef(with_hamza=None):
        rows = [["."] * 8 for _ in range(16)]
        # lam sweeping stroke from upper-right to lower-left
        for i, (x, y) in enumerate([(6, 1), (6, 2), (5, 3), (5, 4), (4, 5), (4, 6),
                                    (3, 7), (3, 8), (2, 9), (2, 10), (1, 11), (1, 12)]):
            rows[y][x] = "#"
        # alef bar on the right side (visual right = end of ligature)
        for y in range(3, 12):
            rows[y][5] = "#" if y > 4 else "#"
        # hamza above alef
        if with_hamza:
            for x in (4, 5, 6):
                rows[1][x] = "#" if with_hamza == "f" else "."
        return ["".join(r) for r in rows]
    # simpler: lam part drawn like lam, alef as a bar at x=6
    def lam_alef2(hamza=None, madda=False):
        rows = [["."] * 8 for _ in range(16)]
        # lam: from top-right down to bottom-left, with bottom curve right
        pts = [(6, 1), (6, 2), (5, 3), (5, 4), (4, 5), (4, 6), (3, 7), (3, 8),
               (2, 9), (2, 10), (1, 11), (0, 12)]
        for x, y in pts:
            rows[y][x] = "#"
        rows[11][0] = "#"
        # alef bar at x=6 (visual right end of the ligature)
        for y in range(2, 11):
            rows[y][6] = "#"
        if hamza:
            rows[0][5] = "#"; rows[0][6] = "#"
            rows[1][6] = "#"
        if madda:
            for x in range(5, 8):
                rows[0][x] = "#"
        return ["".join(r) for r in rows]

    for name, f in (("لا", lam_alef2()), ("لأ", lam_alef2(hamza=True)),
                    ("لإ", lam_alef2(hamza=True)), ("لآ", lam_alef2(madda=True))):
        codes[c] = (name, "LIG")
        art_by_code[c] = f
        c += 1
    return codes, art_by_code

def tile_index(code):
    """ROM tile index for a character code.

    The engine computes the VRAM tile number as
        ((c - 0x20) & 0xE0) * 2 + ((c - 0x20) & 0x1F)
    (see the glyph path at 0x5ade4), i.e. the font is stored in ROM as
    blocks of 32 codes: 32 glyph tiles followed by 32 bottom-half tiles.
    """
    i = (code - 0x20) & 0xFF
    return (i & 0xE0) * 2 + (i & 0x1F)

# ------------------------------------------------------------ tile encode ---
def art16_to_tiles(g):
    """8x16 art -> (top32, bottom32) 4bpp with ink=1."""
    def tile(rows):
        t = bytearray(32)
        for y in range(8):
            for x in range(8):
                if rows[y][x] == "#":
                    bi = y * 4 + x // 2
                    t[bi] |= 1 if x % 2 == 0 else 0x10
        return bytes(t)
    return tile(g[:8]), tile(g[8:])

def art8_from16(g):
    """squash 16-row art into 8 rows (OR of two rows per output row)."""
    out = []
    for r in range(8):
        s = ""
        for x in range(8):
            v = "."
            for y in (r * 2, r * 2 + 1):
                if g[y][x] == "#":
                    v = "#"
            s += v
        out.append(s)
    return out

def art8_to_tile(g):
    t = bytearray(32)
    for y in range(8):
        for x in range(8):
            if g[y][x] == "#":
                bi = y * 4 + x // 2
                t[bi] |= 1 if x % 2 == 0 else 0x10
    return bytes(t)

# ------------------------------------------------------------------- build ---
def main():
    codes, art_by_code = build_code_table()
    data = bytearray(open(ROM, "rb").read())
    if len(data) < 0x400000:
        data.extend(b"\xff" * (0x400000 - len(data)))

    report = []
    for code, (letter, frm) in sorted(codes.items()):
        g16 = art_by_code[code]
        top, bot = art16_to_tiles(g16)
        g8 = art8_from16(g16)
        t8 = art8_to_tile(g8)
        t = tile_index(code)
        # 8x16 fonts: top tile at t, bottom tile at t+32 (block layout)
        for base in (LARGE_BASE, BOLD_BASE):
            off = base + t * 32
            data[off:off + 32] = top
            data[off + 32 * 32: off + 32 * 32 + 32] = bot
        # the 8x8 small font is LINEAR (tile = code - 0x20, codes 0x20-0xFF)
        for fb, fsize in SMALL_FONTS:
            foff = fb + (code - 0x20) * 32
            if foff + 32 <= fb + fsize and foff < len(data):
                data[foff:foff + 32] = t8
        report.append((code, letter, frm))

    os.makedirs(os.path.dirname(OUT_ROM), exist_ok=True)
    open(OUT_ROM, "wb").write(bytes(data))
    print("wrote", OUT_ROM, len(data))
    print("glyph codes: %#x..%#x (%d glyphs)" % (min(codes), max(codes), len(codes)))

    json.dump({"%02X" % c: [codes[c][0], codes[c][1]] for c in codes},
              open(r"C:\Users\reva4\Desktop\game\font\arabic_codes.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
