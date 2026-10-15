import re, json, os

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)
CHARMAP = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\charmap.txt"
OUT = r"C:\Users\reva4\Desktop\game\text"

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

TABLE_AT = 0x117dd4
TABLE_N = 1792
story_lo, story_hi = 0x101200, 0x117dd4

strs = parse_strings(story_lo, story_hi)
by_off = {}
for off, ln, raw in strs:
    by_off[off] = (ln, raw)

# verify each table entry points at a parsed string start
entries = []
missing = 0
for k in range(TABLE_N):
    ta = TABLE_AT + 4 * k
    v = int.from_bytes(data[ta:ta+4], "little")
    off = v - 0x08000000
    if off in by_off:
        entries.append((k, ta, off, by_off[off]))
    else:
        missing += 1
        entries.append((k, ta, off, None))
print("entries:", len(entries), "missing:", missing)

with open(os.path.join(OUT, "dump_story.txt"), "w", encoding="utf-8") as f:
    for k, ta, off, ent in entries:
        if ent:
            ln, raw = ent
            f.write("### %d | tbl=%#x ptr=%#x len=%d\n%s\n" % (k, ta, off, ln, decode(raw)))
        else:
            f.write("### %d | tbl=%#x ptr=%#x MISSING\n" % (k, ta, off))

# stats on lengths
lens = [e[3][0] for e in entries if e[3]]
print("story strings:", len(lens), "max len:", max(lens), "avg:", sum(lens)/len(lens))
