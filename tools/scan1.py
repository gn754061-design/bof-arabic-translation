import sys, collections

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def try_offset(delta):
    # map byte b -> chr(b + delta)
    counts = collections.Counter()
    mapping = {}
    for b in range(256):
        c = b + delta
        if 0x20 <= c < 0x7f:
            mapping[b] = chr(c)
        else:
            mapping[b] = None
    for i in range(0, len(data) - 4):
        window = data[i:i+6]
        s = "".join(mapping.get(b, "\x00") for b in window)
        if None not in [mapping.get(b) for b in window] or True:
            pass
        # score only windows fully printable
        if all(mapping.get(b) is not None for b in window):
            counts[i] = s
    return counts

words = [b"the", b"and", b"you", b"are", b"for"]
best = []
for delta in range(256):
    m = {}
    for b in range(256):
        c = b + delta
        m[b] = chr(c) if 0x20 <= c < 0x7f else None
    # quick scan using raw bytes with offset applied
    score = 0
    for w in words:
        # encode word into this scheme
        enc = bytes(((ch - delta) & 0xff) for ch in w)
        idx = data.find(enc)
        while idx != -1:
            score += 1
            idx = data.find(enc, idx + 1)
    if score > 5:
        best.append((score, delta))

best.sort(reverse=True)
print("top delta candidates:", best[:10])
