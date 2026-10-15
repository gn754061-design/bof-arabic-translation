import re, json, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from bof import data, N, b2c, c2b, controls, decode, parse_strings, is_textlike, OUT

# Regions with lots of text (from extract1), excluding the trailing padding
regions = []
for off in range(0, N, 256):
    pass
# recompute quickly
BLK = 256
scores = []
for off in range(0, N, BLK):
    chunk = data[off:off + BLK]
    sc = sum(1 for b in chunk if b in set(b2c.keys()) | set(range(0x00, 0x0e))) / len(chunk)
    scores.append((off, sc))

cur_start, cur = None, []
for off, sc in scores:
    if sc >= 0.75:
        if cur_start is None:
            cur_start = off
        cur.append(off)
    else:
        if cur_start is not None and len(cur) >= 2:
            regions.append((cur_start, cur[-1] + BLK))
        cur_start, cur = None, []
regions = [(a, b) for a, b in regions if 256 <= b - a and not (a > 0x318000)]

def in_regions(off):
    return any(a <= off < b for a, b in regions)

# parse strings in all regions
region_strings = {}
for a, b in regions:
    strs = parse_strings(a, b)
    keep = {off: (ln, raw) for off, ln, raw in strs if is_textlike(raw)}
    if keep:
        region_strings[(a, b)] = keep

# find pointer tables into any region
hits = []
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    if 0x08000000 <= v < 0x08000000 + N:
        off = v - 0x08000000
        if in_regions(off):
            hits.append((i, off))

tables = []
cur = []
for i, off in hits:
    if cur and i == cur[-1][0] + 4:
        cur.append((i, off))
    else:
        if len(cur) >= 3:
            tables.append(cur)
        cur = [(i, off)]
if len(cur) >= 3:
    tables.append(cur)
tables.sort(key=lambda t: -len(t))
print("regions:", len(regions), "tables:", len(tables))
for t in tables[:40]:
    a = t[0][1]; b = t[-1][1]
    print(f"  tbl@{t[0][0]:#x} n={len(t)} -> {a:#x}..{b:#x} (stride~{(b-a)//max(1,len(t)-1)})")

json.dump([[list(x) for x in t] for t in tables], open(os.path.join(OUT, "tables_all.json"), "w"))
