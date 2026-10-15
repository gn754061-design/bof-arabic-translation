from PIL import Image
import os, json

REF = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\graphics\fonts"
ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def glyph_tiles(name, ink=1, gw=8, gh=8):
    im = Image.open(os.path.join(REF, name + ".png")).convert("L")
    w, h = im.size
    px = im.load()
    cols = w // gw
    out = {}
    for ty in range(h // gh):
        for tx in range(w // gw):
            code = ty * cols + tx
            nbytes = gw * gh // 2
            g = bytearray(nbytes)
            for y in range(gh):
                for x in range(gw):
                    v = px[tx * gw + x, ty * gh + y]
                    idx = ink if v < 250 else 0
                    bi = (y % 8) * 4 + (x // 2)
                    if x % 2 == 0:
                        g[bi] |= idx
                    else:
                        g[bi] |= idx << 4
            out[code] = bytes(g)
    return out, cols

for name, gh in (("large", 16), ("large_bold", 16)):
    glyphs, cols = glyph_tiles(name, gh=gh)
    mapping = {}
    for code, tile in glyphs.items():
        if not any(tile):
            continue
        i = data.find(tile)
        while i != -1:
            nxt = glyphs.get(code + 1)
            if nxt and any(nxt) and data[i + len(tile): i + len(tile) + len(nxt)] == nxt:
                mapping[code] = i
                break
            i = data.find(tile, i + 1)
    print(name, "located:", len(mapping))
    if mapping:
        from collections import Counter
        strides, bases = Counter(), Counter()
        items = sorted(mapping.items())
        for (c1, o1), (c2, o2) in zip(items, items[1:]):
            if c2 > c1:
                strides[(o2 - o1) / (c2 - c1)] += 1
        for c, o in mapping.items():
            pass
        st = strides.most_common(1)[0][0]
        for c, o in mapping.items():
            bases[o - c * st] += 1
        b = bases.most_common(1)[0]
        print("  stride:", st, "base:", hex(int(b[0])), "votes:", b[1], "span:", hex(min(mapping.values())), hex(max(mapping.values())))
        json.dump({str(c): hex(o) for c, o in mapping.items()}, open(r"C:\Users\reva4\Desktop\game\tools\%s_font_map.json" % name, "w"))
