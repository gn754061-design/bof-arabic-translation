import re, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bof import data, N, b2c, decode, parse_strings, is_textlike, OUT

BLK = 256
TEXTBYTES = set(b2c.keys()) | set(range(0x00, 0x0e))
scores = []
for off in range(0, N, BLK):
    chunk = data[off:off + BLK]
    sc = sum(1 for b in chunk if b in TEXTBYTES) / len(chunk)
    scores.append((off, sc))
regions, cur_start, cur = [], None, []
for off, sc in scores:
    if sc >= 0.75:
        if cur_start is None:
            cur_start = off
        cur.append(off)
    else:
        if cur_start is not None and len(cur) >= 2:
            regions.append((cur_start, cur[-1] + BLK))
        cur_start, cur = None, []
regions = [(a, b) for a, b in regions if 256 <= b - a and a < 0x318000]

def in_regions(off):
    return any(a <= off < b for a, b in regions)

hits = []
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    if 0x08000000 <= v < 0x08000000 + N and in_regions(v - 0x08000000):
        hits.append((i, v - 0x08000000))

tables, cur = [], []
for i, off in hits:
    if cur and i == cur[-1][0] + 4:
        cur.append((i, off))
    else:
        if len(cur) >= 3:
            tables.append(cur)
        cur = [(i, off)]
if len(cur) >= 3:
    tables.append(cur)

# build string lookup for all regions
strings_by_region = {}
for a, b in regions:
    strings_by_region[(a, b)] = parse_strings(a, b)

def find_string(off):
    for (a, b), strs in strings_by_region.items():
        if a <= off < b:
            for s_off, ln, raw in strs:
                if s_off == off:
                    return ln, raw
                if s_off < off < s_off + ln:
                    return ln, raw  # mid-string pointer
            return None
    return None

master = []
for t in tables:
    tbl_addr = t[0][0]
    for idx, (ta, off) in enumerate(t):
        ent = find_string(off)
        if ent:
            ln, raw = ent
            master.append({"table": tbl_addr, "idx": idx, "tbl_off": ta, "ptr": off,
                           "len": ln, "text": decode(raw), "mid": off < (ent[0] and 0 or 0) == off and ent is not None})
        else:
            master.append({"table": tbl_addr, "idx": idx, "tbl_off": ta, "ptr": off,
                           "len": 0, "text": None, "mid": None})

json.dump(master, open(os.path.join(OUT, "master.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# summary by table
from collections import Counter
cnt = Counter()
chars = Counter()
for m in master:
    if m["text"]:
        cnt[m["table"]] += 1
        chars[m["table"]] += len(m["text"])
print("tables with text:", len(cnt))
for tbl, c in sorted(cnt.items(), key=lambda x: -x[1]):
    print(f"  {tbl:#x}: {c} strings, {chars[tbl]} chars")
