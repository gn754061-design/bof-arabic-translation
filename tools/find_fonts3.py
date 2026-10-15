from PIL import Image
import os

REF = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\graphics\fonts"
ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def bmp_1bpp(path, code, gw=8, gh=8, rowmajor=True):
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    cols = w // gw
    tx, ty = code % cols, code // cols
    out = bytearray(gw * gh // 8)
    for y in range(gh):
        row = 0
        for x in range(gw):
            v = px[tx * gw + x, ty * gh + y]
            if v < 250:
                row |= 1 << (7 - x) if rowmajor else 1 << y
        if rowmajor:
            out[y] = row
        else:
            for x in range(gw):
                if row & (1 << x):
                    out[x] |= 1 << (7 - y)
    return bytes(out)

def bmp_4bpp(path, code, ink, gw=8, gh=8):
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    cols = w // gw
    tx, ty = code % cols, code // cols
    g = bytearray(gw * gh // 2)
    for y in range(gh):
        for x in range(gw):
            v = px[tx * gw + x, ty * gh + y]
            idx = ink if v < 250 else 0
            bi = (y % 8) * 4 + (x // 2)
            if x % 2 == 0:
                g[bi] |= idx
            else:
                g[bi] |= idx << 4
    return bytes(g)

tests = [
    ("small", 8, 0x2A), ("small", 8, 0x48), ("small", 8, 0x20), ("small", 8, 0x02),
    ("large", 16, 0x2A), ("large", 16, 0x48), ("large", 16, 0x02),
    ("menu", 8, 0x30),
]
for name, gh, code in tests:
    path = os.path.join(REF, name + ".png")
    found = []
    for ink in (1, 2, 3, 0xF):
        t4 = bmp_4bpp(path, code, ink)
        i = data.find(t4)
        if i != -1:
            found.append(("4bpp", ink, hex(i)))
    for pol in (0, 1):
        t = bmp_1bpp(path, code, 8, gh, True)
        if pol:
            t = bytes(0xFF ^ b for b in t)
        i = data.find(t)
        if i != -1:
            found.append(("1bpp-rm", pol, hex(i)))
        t = bmp_1bpp(path, code, 8, gh, False)
        if pol:
            t = bytes(0xFF ^ b for b in t)
        i = data.find(t)
        if i != -1:
            found.append(("1bpp-cm", pol, hex(i)))
    print(name, hex(code), found)
