# -*- coding: utf-8 -*-
"""Render translated strings from the built ROM the way the game draws them."""
from PIL import Image
import sys, json

ROM = r"C:\Users\reva4\Desktop\game\build\bof_arabic_final.gba"
data = open(ROM, "rb").read()
SMALL = 0x22FA68
LARGE = 0x231668
LARGE_BOT = LARGE + 0x1C00

def tile_index(code):
    i = (code - 0x20) & 0xFF
    return (i & 0xE0) * 2 + (i & 0x1F)

def glyph_large(code):
    if code < 0x20 or code > 0xFF:
        return None
    t = tile_index(code)
    top = data[LARGE + t * 32: LARGE + t * 32 + 32]
    bot = data[LARGE + (t + 32) * 32: LARGE + (t + 32) * 32 + 32]
    return top, bot

import json as _json
try:
    RELOC = _json.load(open(r"C:\Users\reva4\Desktop\game\build\reloc.json", encoding="utf-8"))
except Exception:
    RELOC = {}

def resolve(addr):
    """Follow relocations: strings too long for their slot were moved to the
    overflow area and their pointers repointed."""
    key = "%#x" % addr
    if key in RELOC:
        return int(RELOC[key], 16)
    return addr

def draw_string(addr, path, cols=26, rows=3, scale=3, font="large"):
    addr = resolve(addr)
    im = Image.new("L", (cols * 8 * scale, rows * 16 * scale), 255)
    px = im.load()
    x = y = 0
    i = addr
    hung = 0
    while True:
        c = data[i]
        i += 1
        if c == 0x00:
            break
        if c == 0x03:
            x = 0; y += 1
            continue
        if c == 0x09:
            x = 0; y += 1
            continue
        if c in (0x04, 0x05, 0x07, 0x08):
            x += 0
            continue
        if c in (0x06, 0x0A, 0x0B, 0x0C, 0x0D):
            i += 1  # skip arg
            x += 1
            continue
        g = glyph_large(c)
        if g is None:
            x += 1
            if x >= cols:
                x = 0
                y += 1
            continue
        top, bot = g
        for ti, tile in enumerate((top, bot)):
            for yy in range(8):
                for xx in range(8):
                    b = tile[yy * 4 + xx // 2]
                    v = (b & 0xF) if xx % 2 == 0 else (b >> 4)
                    if v:
                        for dy in range(scale):
                            for dx in range(scale):
                                px[(x * 8 + xx) * scale + dx, (y * 16 + ti * 8 + yy) * scale + dy] = 0
        x += 1
        if x >= cols:
            x = 0; y += 1
        if y >= rows:
            break
        hung += 1
        if hung > 400:
            break
    im.save(path)
    print("rendered", path)

if __name__ == "__main__":
    for a in (0x101238, 0x1012a6, 0x1014a5, 0x1014f0):
        draw_string(a, r"C:\Users\reva4\Desktop\game\font\prev_%x.png" % a)
