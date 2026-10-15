import re, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bof import data, N, b2c, controls, decode

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK

def quality(raw):
    if len(raw) < 4:
        return 0
    good = sum(1 for b in raw if b in PRINTABLE)
    bad = sum(1 for b in raw if b not in ALLOWED)
    if bad > len(raw) * 0.25:
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

# --- regions: blocks where >=80% bytes are allowed (letters/punct/controls)
BLK = 256
scores = []
for off in range(0, N, BLK):
    chunk = data[off:off + BLK]
    sc = sum(1 for b in chunk if b in ALLOWED) / len(chunk)
    scores.append((off, sc))
regions, cur_start, cur = [], None, []
for off, sc in scores:
    if sc >= 0.80:
        if cur_start is None:
            cur_start = off
        cur.append(off)
    else:
        if cur_start is not None and len(cur) >= 4:
            regions.append((cur_start, cur[-1] + BLK))
        cur_start, cur = None, []
if cur_start is not None and len(cur) >= 4:
    regions.append((cur_start, cur[-1] + BLK))
# expand each region by one block on each side to catch boundary strings
regions = [(max(0, a - BLK), min(N, b + BLK)) for a, b in regions if b - a >= 512]
regions = [(a, b) for a, b in regions if a < 0x318000]
print("regions:", len(regions), "total bytes:", sum(b - a for a, b in regions))

strings = {}
for a, b in regions:
    for off, ln, raw in parse_strings(a, b):
        q = quality(raw)
        if q >= 0.6:
            strings[off] = (ln, raw, q)
print("strings:", len(strings))

# --- pointers into any region
def in_regions(off):
    return any(a <= off < b for a, b in regions)

hits = []
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    if 0 <= off < N and in_regions(off) and off in strings:
        hits.append((i, off))

tables, cur = [], []
last_i = None
for i, off in hits:
    if cur and last_i is not None and i - last_i <= 4 * 9:  # allow up to 8 missing entries
        cur.append((i, off))
    else:
        if len(cur) >= 4:
            tables.append(cur)
        cur = [(i, off)]
    last_i = i
if len(cur) >= 4:
    tables.append(cur)

clean = []
for t in tables:
    good = sum(1 for _, off in t if strings.get(off, (0, b"", 0))[2] >= 0.8)
    if good / len(t) >= 0.6:
        clean.append(t)
clean.sort(key=lambda t: -len(t))
print("tables:", len(tables), "clean:", len(clean), "entries:", sum(len(t) for t in clean))

master = []
for t in clean:
    tbl = t[0][0]
    for idx, (ta, off) in enumerate(t):
        ent = strings.get(off)
        if ent and ent[2] >= 0.8:
            ln, raw, q = ent
            master.append({"table": tbl, "idx": idx, "tbl_off": ta, "ptr": off,
                           "len": ln, "text": decode(raw)})
        else:
            master.append({"table": tbl, "idx": idx, "tbl_off": ta, "ptr": off,
                           "len": 0, "text": None})
json.dump(master, open(r"C:\Users\reva4\Desktop\game\text\master.json", "w", encoding="utf-8"), ensure_ascii=False)

from collections import Counter
cnt = Counter(m["table"] for m in master if m["text"])
for tbl, c in sorted(cnt.items(), key=lambda x: -x[1])[:30]:
    print(f"  {tbl:#x}: {c}")
