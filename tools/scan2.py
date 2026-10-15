ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
delta = 25

def dec(bs):
    out = []
    for b in bs:
        c = b + delta
        out.append(chr(c) if 0x20 <= c < 0x7f else "\x00")
    return "".join(out)

for w in ["the ", "and ", "you ", "Ryu", "Drogen", "Nina", "castle", "dragon"]:
    enc = bytes((ord(ch) - delta) for ch in w)
    idx = data.find(enc)
    print(w, hex(idx))

# dump region around first 'the ' hit
enc = bytes((ord("the ") - delta) for ch in "the ")
idx = data.find(enc)
print("=== first hits ===")
for k in range(6):
    i = data.find(enc, idx if k == 0 else idx + 1)
    idx = i
    if i == -1:
        break
    print(hex(i), dec(data[i:i+80]))
