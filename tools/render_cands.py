from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def render_tiles(start, count, cols, path, hgt=8):
    im = Image.new("L", (cols * 8, ((count + cols - 1) // cols) * hgt), 255)
    px = im.load()
    for t in range(count):
        tx, ty = t % cols, t // cols
        base = start + t * 32
        for y in range(8):
            for x in range(8):
                bi = y * 4 + x // 2
                b = data[base + bi]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                px[tx * 8 + x, ty * hgt + (y % hgt)] = 255 if v == 0 else 0
    im.save(path)
    print(path, im.size)

render_tiles(0x231500, 448, 16, r"C:\Users\reva4\Desktop\game\font\cand_231500.png")
render_tiles(0x234e80, 256, 16, r"C:\Users\reva4\Desktop\game\font\cand_234e80.png")
render_tiles(0x282300, 256, 16, r"C:\Users\reva4\Desktop\game\font\cand_282300.png")
