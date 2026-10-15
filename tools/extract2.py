import re, json
from collections import defaultdict

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)
CHARMAP = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\charmap.txt"

b2c, c2b, controls = {}, {}, {}
for line in open(CHARMAP, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip() or line.strip().startswith("@"):
        continue
    m = re.match(r"'(.*)'\s*=\s*([0-9A-Fa-f]+)", line)
    if m:
        ch, val = m.group(1), int(m.group(2), 16)
        if ch == "\\n":
            ch = "\n"
        b2c[val] = ch
        continue
    m = re.match(r"(\w+)\s*=\s*([0-9A-Fa-f]+)", line)
    if m:
        controls[m.group(1)] = int(m.group(2), 16)

CTRL_NAMES = {v: k for k, v in controls.items()}
TEXTBYTES = set(b2c.keys()) | set(range(0x00, 0x0e))

def decode(bs):
    out = []
    for b in bs:
        if b in b2c:
            out.append(b2c[b])
        elif b in CTRL_NAMES:
            out.append("{%s}" % CTRL_NAMES[b])
        else:
            out.append("{%02X}" % b)
    return "".join(out)

def parse_strings(a, b):
    """Parse region [a,b) into (offset, length_including_terminator, raw) strings."""
    res = []
    i = a
    while i < b:
        start = i
        while i < b and data[i] != 0x00:
            i += 1
        if i < b:
            i += 1  # include terminator
        res.append((start, i - start, data[start:i]))
        if i >= b:
            break
    return res

# main story region
REGIONS = {
    "story": (0x101200, 0x117e00),
}

def is_textlike(raw):
    letters = sum(1 for b in raw if 0x2a <= b <= 0x61)
    return letters >= 3

all_strings = {}
for name, (a, b) in REGIONS.items():
    strs = parse_strings(a, b)
    keep = [(off, ln, raw) for off, ln, raw in strs if is_textlike(raw)]
    all_strings[name] = keep
    print(name, "strings:", len(keep), "bytes:", sum(ln for _, ln, _ in keep))

# Pointer scan: find 4-byte LE values 0x08000000+off where off in any region
region_ranges = list(REGIONS.values())
def in_region(off):
    for a, b in region_ranges:
        if a <= off < b:
            return (a, b)
    return None

pointer_hits = []
for i in range(0, N - 4, 2):  # aligned scan first
    v = data[i] | (data[i+1] << 8) | (data[i+2] << 16) | (data[i+3] << 24)
    if 0x08000000 <= v < 0x08000000 + N:
        off = v - 0x08000000
        if in_region(off):
            pointer_hits.append((i, off))

print("aligned pointer hits:", len(pointer_hits))

# find tables: consecutive pointers every 4 bytes
tables = []
cur = []
for i, off in pointer_hits:
    if cur and i == cur[-1][0] + 4:
        cur.append((i, off))
    else:
        if len(cur) >= 4:
            tables.append(cur)
        cur = [(i, off)]
if len(cur) >= 4:
    tables.append(cur)
tables.sort(key=lambda t: -len(t))
print("pointer tables (>=4 entries):", len(tables))
for t in tables[:20]:
    print(f"  table@{t[0][0]:#x} entries={len(t)} -> range {t[0][1]:#x}..{t[-1][1]:#x}")

json.dump({"tables": [[list(x) for x in t] for t in tables]}, open(r"C:\Users\reva4\Desktop\game\tools\tables.json", "w"))
