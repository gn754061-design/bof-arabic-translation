from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def render(start, count, cols, path, gh=8, scale=1, tbs=32, gh_cells=1):
    rows = (count + cols - 1) // cols
    im = Image.new("L", (cols * 8 * scale, rows * gh * scale * gh_cells), 200)
    px = im.load()
    for g in range(count):
        tx, ty = g % cols, g // cols
        base = start + g * (gh * 8 // 2) * gh_cells
        for y in range(gh * gh_cells):
            tile = y // 8
            for x in range(8):
                bi = (y % 8) * 4 + x // 2
                b = data[base + tile * tbs + bi]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                col = 0 if v == 0 else 255
                for dy in range(scale):
                    for dx in range(scale):
                        px[(tx * 8 + x) * scale + dx, (ty * gh * gh_cells + y) * scale + dy] = col
    im.save(path)
    print(path, im.size)

# full large-font area as 8x16 glyphs, 16 columns
render(0x231668, 224, 16, r"C:\Users\reva4\Desktop\game\font\large_full.png", gh=8, scale=1, gh_cells=2)
