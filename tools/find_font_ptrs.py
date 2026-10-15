ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

def find_ptr(target):
    v = 0x08000000 + target
    pat = v.to_bytes(4, "little")
    res = []
    i = data.find(pat)
    while i != -1:
        res.append(i)
        i = data.find(pat, i + 1)
    return res

for name, off in (("small_font", 0x22FA48), ("run231500", 0x231500), ("run234e80", 0x234e80), ("run282300", 0x282300), ("menufont", 0xf3ea8)):
    print(name, hex(off), [hex(x) for x in find_ptr(off)])
