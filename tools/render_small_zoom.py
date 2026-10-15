from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def render(start, count, cols, path, gh=8, scale=2):
    rows = (count + cols - 1) // cols
    im = Image.new("L", (cols * 8 * scale, rows * gh * scale), 200)
    px = im.load()
    for g in range(count):
        tx, ty = g % cols, g // cols
        base = start + g * (gh * 8 // 2)
        for y in range(gh):
            tile = y // 8
            for x in range(8):
                bi = (y % 8) * 4 + x // 2
                b = data[base + tile * 32 + bi]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                col = 0 if v == 0 else 255
                for dy in range(scale):
                    for dx in range(scale):
                        px[(tx * 8 + x) * scale + dx, (ty * gh + y) * scale + dy] = col
    im.save(path)
    print(path, im.size)

render(0x22FA48, 96, 12, r"C:\Users\reva4\Desktop\game\font\small_zoom.png")
