import re, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bof import data, N, b2c, controls, decode

TEXTBYTES = set(b2c.keys()) | set(range(0x00, 0x0e))
CTRL = set(range(0x00, 0x0e))

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK

def string_quality(raw):
    if len(raw) < 4:
        return 0
    good = sum(1 for b in raw if b in PRINTABLE)
    bad = sum(1 for b in raw if b not in ALLOWED)
    if bad > len(raw) * 0.10:
        return 0
    letters = sum(1 for b in raw if 0x2a <= b <= 0x61)
    if letters < 3:
        return 0
    return good / len(raw)

def parse_strings(a, b):
    res = []
    i = a
    while i < b:
        start = i
        while i < b and data[i] != 0x00:
            i += 1
        if i < b:
            i += 1
        res.append((start, i - start, data[start:i]))
        if i >= b:
            break
    return res

# rebuild regions from scratch using strict scoring
BLK = 256
scores = []
for off in range(0, N, BLK):
    chunk = data[off:off + BLK]
    sc = sum(1 for b in chunk if b in ALLOWED) / len(chunk)
    scores.append((off, sc))

regions, cur_start, cur = [], None, []
for off, sc in scores:
    if sc >= 0.85:
        if cur_start is None:
            cur_start = off
        cur.append(off)
    else:
        if cur_start is not None and len(cur) >= 4:
            regions.append((cur_start, cur[-1] + BLK))
        cur_start, cur = None, []
if cur_start is not None and len(cur) >= 4:
    regions.append((cur_start, cur[-1] + BLK))
regions = [(a, b) for a, b in regions if b - a >= 512 and a < 0x318000]
print("strict regions:", len(regions))

all_strings = {}
for a, b in regions:
    for off, ln, raw in parse_strings(a, b):
        if string_quality(raw) >= 0.8:
            all_strings[off] = (ln, raw)
print("strict strings:", len(all_strings))

def in_regions(off):
    return any(a <= off < b for a, b in regions)

hits = []
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    if 0 <= off < N and in_regions(off) and off in all_strings:
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

# keep tables where >=70% entries are clean strings
good_tables = []
for t in tables:
    ok = sum(1 for _, off in t if off in all_strings)
    if ok / len(t) >= 0.7:
        good_tables.append(t)
good_tables.sort(key=lambda t: -len(t))
print("tables:", len(tables), "clean:", len(good_tables))
total = sum(len(t) for t in good_tables)
print("total entries in clean tables:", total)

master = []
for t in good_tables:
    tbl = t[0][0]
    for idx, (ta, off) in enumerate(t):
        ent = all_strings.get(off)
        if ent:
            ln, raw = ent
            master.append({"table": tbl, "idx": idx, "tbl_off": ta, "ptr": off,
                           "len": ln, "text": decode(raw)})
        else:
            master.append({"table": tbl, "idx": idx, "tbl_off": ta, "ptr": off,
                           "len": 0, "text": None})
json.dump(master, open(r"C:\Users\reva4\Desktop\game\text\master.json", "w", encoding="utf-8"), ensure_ascii=False)
from collections import Counter
cnt = Counter(m["table"] for m in master if m["text"])
for tbl, c in sorted(cnt.items(), key=lambda x: -x[1])[:25]:
    print(f"  {tbl:#x}: {c}")
