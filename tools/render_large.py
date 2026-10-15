from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def render(start, count, cols, path, gh=16):
    rows = (count + cols - 1) // cols
    im = Image.new("L", (cols * 8, rows * gh), 255)
    px = im.load()
    for g in range(count):
        tx, ty = g % cols, g // cols
        base = start + g * (gh * 4)  # 8*gh px = 32*gh/8 bytes = 4*gh bytes
        for y in range(gh):
            tile = y // 8
            for x in range(8):
                bi = (y % 8) * 4 + x // 2
                b = data[base + tile * 32 + bi]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                px[tx * 8 + x, ty * gh + y] = 255 if v == 0 else 0
    im.save(path)
    print(path, im.size)

render(0x231668, 112, 16, r"C:\Users\reva4\Desktop\game\font\large_try.png")
render(0x234e68, 112, 16, r"C:\Users\reva4\Desktop\game\font\kanji_try.png")
