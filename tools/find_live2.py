import sys, json
sys.path.insert(0, r"C:\Users\reva4\Desktop\game\tools")
from bof import data, N, decode

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK

def quality(raw):
    if len(raw) < 4:
        return 0.0
    if sum(1 for b in raw if 0x2a <= b <= 0x61) < 3:
        return 0.0
    return 1.0 - (sum(1 for b in raw if b not in ALLOWED) / len(raw))

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
print("regions:", len(regions), "strings:", len(strings))

# positions that hold a pointer into any text region
is_ptr = {}
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    if in_regions(off):
        is_ptr[i] = off

# which ROM offsets are referenced by code (as 0x08xxxxxx values)?
code_ref_targets = set()
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    if 0x08000000 <= v < 0x08000000 + N:
        code_ref_targets.add(v - 0x08000000)

# table starts: pointer positions whose previous 4-byte is not a pointer
starts = []
for i in sorted(is_ptr):
    if (i - 4) not in is_ptr:
        starts.append(i)
print("table starts:", len(starts))

# live tables: any code-referenced position near text pointers seeds a table
seed_positions = set()
for p in code_ref_targets:
    for d in (-8, -4, 0, 4, 8):
        if (p + d) in is_ptr:
            seed_positions.add(p + d)
            break
print("seed positions:", len(seed_positions), [hex(s) for s in sorted(seed_positions)])

def expand(s):
    # backward
    a = s
    while (a - 4) in is_ptr:
        a -= 4
    # forward with gap tolerance
    b = s
    gap = 0
    while b + 4 < N - 4 and gap <= 16:
        nxt = b + 4
        if nxt in is_ptr:
            b = nxt
            gap = 0
        else:
            gap += 4
            if gap > 16:
                break
            b = nxt
    return a, b

spans = {}
for s in seed_positions:
    a, b = expand(s)
    key = a
    if key not in spans or b - a > spans[key][1] - spans[key][0]:
        spans[key] = (a, b)

live = []
for key, (a, b) in sorted(spans.items()):
    run = [(i, is_ptr[i]) for i in range(a, b + 1, 4) if i in is_ptr]
    if len(run) >= 8:
        live.append(run)
print("live tables:", len(live))
tot = 0
for t in sorted(live, key=lambda x: -len(x)):
    print("  %#x: %d entries -> %#x..%#x" % (t[0][0], len(t), t[0][1], t[-1][1]))
    tot += len(t)
print("live entries:", tot)
json.dump([[list(x) for x in t] for t in live], open(r"C:\Users\reva4\Desktop\game\tools\live_tables.json", "w"))
