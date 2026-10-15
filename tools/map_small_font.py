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

small, cols = glyph_tiles("small")
print("small glyphs:", len(small), "cols:", cols)

mapping = {}
for code, tile in small.items():
    i = data.find(tile)
    # verify with next glyph
    ok = False
    while i != -1:
        nxt = small.get(code + 1)
        if nxt is None or data[i + 32:i + 64] == nxt:
            ok = True
            break
        i = data.find(tile, i + 1)
    if ok and i != -1:
        mapping[code] = i

tiles = sorted(((i, c) for c, i in mapping.items()))
print("located:", len(mapping))
print("tile span:", hex(tiles[0][0]), "-", hex(tiles[-1][0]))
# deduce base & stride
base0, stride = None, None
if len(tiles) >= 2:
    diffs = {}
    for (o1, c1), (o2, c2) in zip(tiles, tiles[1:]):
        if c2 > c1:
            d = (o2 - o1) / (c2 - c1)
            diffs[d] = diffs.get(d, 0) + 1
    print("stride candidates:", sorted(diffs.items(), key=lambda x: -x[1])[:5])
    stride = sorted(diffs.items(), key=lambda x: -x[1])[0][0]
    # base = o - code*stride
    bases = {}
    for c, o in mapping.items():
        b = o - c * stride
        bases[b] = bases.get(b, 0) + 1
    print("base candidates:", sorted(bases.items(), key=lambda x: -x[1])[:5])

json.dump({str(c): hex(o) for c, o in mapping.items()}, open(r"C:\Users\reva4\Desktop\game\tools\small_font_map.json", "w"))
