import sys, os
sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(__file__), "extract_final.py"), encoding="utf-8").read()
head = src.split("# --- pointers")[0]
exec(compile(head, "head", "exec"))

def in_regions(off):
    return any(a <= off < b for a, b in regions)

hits = []
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    if 0 <= off < N and in_regions(off) and off in strings:
        hits.append((i, off))

tables, cur = [], []
for i, off in hits:
    if cur and i == cur[-1][0] + 4:
        cur.append((i, off))
    else:
        if len(cur) >= 4:
            tables.append(cur)
        cur = [(i, off)]
if len(cur) >= 4:
    tables.append(cur)

tables.sort(key=lambda t: -len(t))
print("tables:", len(tables))
for t in tables[:12]:
    print("  start %#x entries %d -> %#x" % (t[0][0], len(t), t[0][1]))
