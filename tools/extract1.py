import re, json, sys
from collections import Counter, defaultdict

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

CHARMAP = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\charmap.txt"

def load_charmap():
    b2c, c2b = {}, {}
    controls = {}
    for line in open(CHARMAP, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.strip().startswith("#") or line.strip().startswith("@"):
            if line.strip().startswith("@") and "control" in line:
                mode = "ctrl"
                continue
            if line.strip().startswith("@") and "player" in line:
                break
            continue
        m = re.match(r"'(.*)'\s*=\s*([0-9A-Fa-f]+)", line)
        if m:
            ch, val = m.group(1), int(m.group(2), 16)
            if ch == "\\n":
                ch = "\n"
            elif ch == "\\0":
                ch = "\x00"
            b2c[val] = ch
            c2b.setdefault(ch, val)
            continue
        m = re.match(r"(\w+)\s*=\s*([0-9A-Fa-f]+)", line)
        if m:
            controls[m.group(1)] = int(m.group(2), 16)
    return b2c, c2b, controls

b2c, c2b, controls = load_charmap()
print("charmap bytes:", len(b2c), "controls:", controls)

# valid text bytes: everything in b2c plus control-code range
TEXTBYTES = set(b2c.keys()) | set(range(0x00, 0x0e))
# score blocks
BLK = 256
scores = []
for off in range(0, N, BLK):
    chunk = data[off:off + BLK]
    if not chunk:
        break
    sc = sum(1 for b in chunk if b in TEXTBYTES)
    scores.append((off, sc / len(chunk)))

# find contiguous regions with avg score > 0.75
regions = []
cur_start = None
cur = []
for off, sc in scores:
    if sc >= 0.75:
        if cur_start is None:
            cur_start = off
        cur.append((off, sc))
    else:
        if cur_start is not None and len(cur) >= 4:
            regions.append((cur_start, cur[-1][0] + BLK, sum(s for _, s in cur) / len(cur)))
        cur_start = None
        cur = []
if cur_start is not None and len(cur) >= 4:
    regions.append((cur_start, cur[-1][0] + BLK, sum(s for _, s in cur) / len(cur)))

print("text regions (>=1KB):")
for a, b, s in regions:
    if b - a >= 1024:
        print(f"  {a:#08x}-{b:#08x} len={b-a:#x} avg={s:.2f}")

json.dump({"regions": [(a, b) for a, b, s in regions if b - a >= 1024]}, open(r"C:\Users\reva4\Desktop\game\tools\regions.json", "w"))
