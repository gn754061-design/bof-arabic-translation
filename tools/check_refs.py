import json

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

master = json.load(open(r"C:\Users\reva4\Desktop\game\text\master.json", encoding="utf-8"))

# text string regions (where strings live)
str_regions = []
for m in master:
    if m["text"]:
        str_regions.append((m["ptr"], m["ptr"] + m["len"]))
str_regions.sort()
# merge
merged = []
for a, b in str_regions:
    if merged and a <= merged[-1][1] + 64:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
print("string regions:", [(hex(a), hex(b)) for a, b in merged])

# scan ALL byte offsets for pointers into these regions
hits = []
for i in range(0, N - 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    if 0 <= off < N:
        for a, b in merged:
            if a <= off < b:
                hits.append((i, off))
                break
print("total pointer refs into text regions:", len(hits))

# which refs are NOT in our master tables?
known_tbl_offsets = set(m["tbl_off"] for m in master)
refs_outside = [(i, o) for i, o in hits if i not in known_tbl_offsets]
print("refs outside known tables:", len(refs_outside))
from collections import Counter
c = Counter(i >> 16 for i, o in refs_outside)
print("by 64K bank:", sorted(c.items()))

json.dump([[i, o] for i, o in refs_outside], open(r"C:\Users\reva4\Desktop\game\tools\refs_outside.json", "w"))
