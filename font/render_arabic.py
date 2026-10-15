from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\build\bof_arabic.gba"
data = open(ROM, "rb").read()
SMALL = 0x22FA68
LARGE = 0x231668
LARGE_BOT = LARGE + 0x1C00

import json
codes = json.load(open(r"C:\Users\reva4\Desktop\game\font\arabic_codes.json", encoding="utf-8"))
items = sorted((int(k, 16), v) for k, v in codes.items())

def render(per_row, path, large=True, cell_h=16):
    n = len(items)
    rows = (n + per_row - 1) // per_row
    im = Image.new("L", (per_row * 9, rows * (cell_h + 4)), 255)
    px = im.load()
    for i, (code, (letter, frm)) in enumerate(items):
        tx, ty = i % per_row, i // per_row
        if large:
            top = data[LARGE + (code - 0x20) * 32: LARGE + (code - 0x20) * 32 + 32]
            bot = data[LARGE_BOT + (code - 0x20) * 32: LARGE_BOT + (code - 0x20) * 32 + 32]
            tiles = [top, bot]
        else:
            t = data[SMALL + (code - 0x20) * 32: SMALL + (code - 0x20) * 32 + 32]
            tiles = [t]
        for ti, tile in enumerate(tiles):
            for y in range(8):
                for x in range(8):
                    b = tile[y * 4 + x // 2]
                    v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                    if v:
                        px[tx * 9 + x, ty * (cell_h + 4) + ti * 8 + y] = 0
    im.save(path)
    print(path, im.size)

render(15, r"C:\Users\reva4\Desktop\game\font\arabic_large_sheet.png", True, 18)
render(20, r"C:\Users\reva4\Desktop\game\font\arabic_small_sheet.png", False, 12)
