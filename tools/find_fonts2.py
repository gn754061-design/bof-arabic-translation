from PIL import Image
import os

REF = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\graphics\fonts"
ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def png_glyphs(path, ink_val, bg_val, gw=8, gh=8):
    """Return list of glyph byte-blocks in row-major tile order from a font sheet."""
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    nbytes = gw * gh // 2
    glyphs = []
    for ty in range(h // gh):
        for tx in range(w // gw):
            g = bytearray(nbytes)
            for y in range(gh):
                for x in range(gw):
                    v = px[tx * gw + x, ty * gh + y]
                    idx = ink_val if v < 250 else bg_val
                    bi = (y % 8) * 4 + (x // 2)
                    if x % 2 == 0:
                        g[bi] |= idx
                    else:
                        g[bi] |= idx << 4
            glyphs.append(bytes(g))
    return glyphs

def try_locate(name, gh, code):
    path = os.path.join(REF, name + ".png")
    for ink, bg in ((1, 0), (0, 1), (2, 0), (0, 2), (3, 0), (0, 3), (15, 0), (0, 15), (3, 1), (1, 3)):
        glyphs = png_glyphs(path, ink, bg, 8, gh)
        tile = glyphs[code]
        idx = data.find(tile)
        while idx != -1:
            # verify next glyph (code+1) follows immediately
            nxt = glyphs[code + 1]
            if data[idx + len(tile): idx + len(tile) + len(nxt)] == nxt:
                return (ink, bg, idx, len(glyphs))
            idx = data.find(tile, idx + 1)
    return None

tests = [("small", 8, 0x2A), ("small", 8, 0x48), ("large", 16, 0x2A), ("large", 16, 0x48),
         ("large_bold", 16, 0x2A), ("menu", 8, 0x30), ("kanji", 16, 0x00)]
for name, gh, code in tests:
    print(name, hex(code), try_locate(name, gh, code))
