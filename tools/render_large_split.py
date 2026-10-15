from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
BASE = 0x231668

def render_split(start, count, cols, path, scale=2):
    """Hypothesis: top tiles contiguous, then bottom tiles."""
    rows = (count + cols - 1) // cols
    im = Image.new("L", (cols * 8 * scale, rows * 16 * scale), 200)
    px = im.load()
    for g in range(count):
        tx, ty = g % cols, g // cols
        top = start + g * 32
        bot = start + 224 * 32 + g * 32
        for y in range(16):
            src = top if y < 8 else bot
            for x in range(8):
                bi = (y % 8) * 4 + x // 2
                b = data[src + bi]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                col = 0 if v == 0 else 255
                for dy in range(scale):
                    for dx in range(scale):
                        px[(tx * 8 + x) * scale + dx, (ty * 16 + y) * scale + dy] = col
    im.save(path)
    print(path, im.size)

render_split(BASE, 224, 16, r"C:\Users\reva4\Desktop\game\font\large_split.png")
