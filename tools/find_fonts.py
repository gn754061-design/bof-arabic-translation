from PIL import Image
import os, json

REF = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\graphics\fonts"
ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def png_to_tiles(path, ink_val, bg_val, tilew=8, tileh=8):
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    tiles = []
    for ty in range(h // tileh):
        for tx in range(w // tilew):
            t = bytearray(32)
            for y in range(tileh):
                for x in range(tilew):
                    v = px[tx * 8 + x, ty * 8 + y]
                    idx = ink_val if v < 250 else bg_val
                    # 4bpp: byte holds 2 pixels (low nibble = left pixel)
                    byte_i = y * 4 + (x // 2)
                    if x % 2 == 0:
                        t[byte_i] |= idx
                    else:
                        t[byte_i] |= idx << 4
            tiles.append(bytes(t))
    return tiles, (w // 8, h // 8)

def find_font(name, tileh=8):
    path = os.path.join(REF, name + ".png")
    for ink, bg in ((1, 0), (0, 1), (2, 0), (0, 2), (3, 0), (0, 3), (15, 0), (0, 15), (3, 1)):
        tiles, dims = png_to_tiles(path, ink, bg, 8, tileh)
        # build needle from first 48 tiles (codes 0x00..0x2F)
        needle = b"".join(tiles[:48])
        idx = data.find(needle)
        if idx != -1:
            # measure length: how many consecutive tiles match
            n = 0
            while idx + (n + 1) * 32 <= len(data) and data[idx + n * 32: idx + (n + 1) * 32] == tiles[n % len(tiles)] if n < len(tiles) else False:
                n += 1
            return name, (ink, bg), idx, dims, len(tiles)
    return name, None, -1, None, None

for name, th in (("small", 8), ("large", 16), ("large_bold", 16), ("menu", 8), ("kanji", 16)):
    print(find_font(name, th))
