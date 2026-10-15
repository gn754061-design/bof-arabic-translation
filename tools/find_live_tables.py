import sys, json
sys.path.insert(0, r"C:\Users\reva4\Desktop\game\tools")
from bof import data, N, decode

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK
BAD = bytes(b for b in range(256) if b not in ALLOWED)

def quality(raw):
    if len(raw) < 4:
        return 0.0
    if sum(1 for b in raw if b in PRINTABLE and 0x2a <= b <= 0x61) < 3:
        return 0.0
    return 1.0 - (sum(1 for b in raw if b not in ALLOWED) / len(raw))

# text regions
BLK = 256
scores = [(off, sum(1 for b in data[off:off+BLK] if b in ALLOWED) / BLK) for off in range(0, N, BLK)]
regions, cur_start, cur = [], None, []
for off, sc in scores:
    if sc >= 0.75:
        if cur_start is None:
            cur_start = off
        cur.append(off)
    else:
        if cur_start is not None and len(cur) >= 4:
            regions.append((cur_start, cur[-1] + BLK))
        cur_start, cur = None, []
if cur_start is not None and len(cur) >= 4:
    regions.append((cur_start, cur[-1] + BLK))
regions = [(max(0, a - BLK), min(N, b + BLK)) for a, b in regions if b - a >= 512 and a < 0x318000]

def in_regions(off):
    return any(a <= off < b for a, b in regions)

# strings
strings = {}
for a, b in regions:
    i = a
    while i < b:
        start = i
        while i < b and data[i] != 0x00:
            i += 1
        if i < b:
            i += 1
        raw = data[start:i]
        if quality(raw) >= 0.6:
            strings[start] = (i - start, raw)
        if i >= b:
            break

# all pointers
ptrs = {}
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    if off in strings:
        ptrs.setdefault(off, []).append(i)

# table candidates: runs of aligned pointers, gap-tolerant
entries = sorted(ptrs.items())
tables, cur, last = [], [], None
for off, positions in entries:
    for p in positions:
        if cur and last is not None and p - last <= 40:
            cur.append((p, off))
        else:
            if len(cur) >= 8:
                tables.append(cur)
            cur = [(p, off)]
        last = p
if len(cur) >= 8:
    tables.append(cur)

# which table starts are referenced by code (live)?
live = []
for t in tables:
    start = t[0][0]
    pat = (0x08000000 + start).to_bytes(4, "little")
    if data.find(pat) != -1:
        live.append(t)

print("regions:", len(regions), "strings:", len(strings), "tables:", len(tables), "live:", len(live))
tot = 0
for t in sorted(live, key=lambda x: -len(x))[:40]:
    print("  live table %#x: %d entries -> %#x..%#x" % (t[0][0], len(t), t[0][1], t[-1][1]))
    tot += len(t)
print("live entries total:", tot)
json.dump([[list(x) for x in t] for t in live], open(r"C:\Users\reva4\Desktop\game\tools\live_tables.json", "w"))
