from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def render_tiles(start, count, cols, path, label=""):
    im = Image.new("L", (cols * 8, ((count + cols - 1) // cols) * 8), 255)
    px = im.load()
    for t in range(count):
        tx, ty = t % cols, t // cols
        base = start + t * 32
        for y in range(8):
            for x in range(8):
                bi = y * 4 + x // 2
                b = data[base + bi]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                px[tx * 8 + x, ty * 8 + y] = 255 if v == 0 else 0
    im.save(path)
    print(label, "->", path, im.size)

render_tiles(0x22fa48, 400, 32, r"C:\Users\reva4\Desktop\game\font\small_region.png", "small")
render_tiles(0x2316a8, 400, 32, r"C:\Users\reva4\Desktop\game\font\large_region.png", "large")
