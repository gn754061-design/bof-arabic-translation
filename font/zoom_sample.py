from PIL import Image

ROM = r"C:\Users\reva4\Desktop\game\build\bof_arabic.gba"
data = open(ROM, "rb").read()
LARGE = 0x231668
LARGE_BOT = LARGE + 0x1C00

codes = [0x80, 0x81, 0x82, 0x83,   # ب ISO INIT MEDI FIN
         0x9C, 0x9D, 0x9E, 0x9F,   # ل forms (0x80+22*4=0xB8?) - compute below
         0xB8, 0xB9, 0xBA, 0xBB]
# ب index 0 -> 0x80..0x83 ; ل is index? DUAL order: ب(0) ت(1) ث(2) ج(3) ح(4) خ(5) س(6) ش(7) ص(8) ض(9) ط(10) ع(11) غ(12) ف(13) ق(14) ك(15) ل(16) م(17) ن(18) ه(19) ي(20) ئ(21)
codes = [0x80 + 16 * 4 + i for i in range(4)]  # ل forms
names = ["ل-ISO", "ل-INIT", "ل-MEDI", "ل-FIN"]
codes2 = [0x80 + i for i in range(4)]
names2 = ["ب-ISO", "ب-INIT", "ب-MEDI", "ب-FIN"]

im = Image.new("L", (8 * 26, 22 * 2), 255)
px = im.load()
for i, (code, nm) in enumerate(zip(codes + codes2, names + names2)):
    tx, ty = i % 4, i // 4
    top = data[LARGE + (code - 0x20) * 32: LARGE + (code - 0x20) * 32 + 32]
    bot = data[LARGE_BOT + (code - 0x20) * 32: LARGE_BOT + (code - 0x20) * 32 + 32]
    for ti, tile in enumerate((top, bot)):
        for y in range(8):
            for x in range(8):
                b = tile[y * 4 + x // 2]
                v = (b & 0xF) if x % 2 == 0 else (b >> 4)
                if v:
                    px[tx * 26 + x, ty * 24 + ti * 8 + y] = 0
im.save(r"C:\Users\reva4\Desktop\game\font\zoom_b Lam.png")
print("ok")
