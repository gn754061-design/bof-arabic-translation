import re, json, os, sys

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
CHARMAP = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\charmap.txt"
OUT = r"C:\Users\reva4\Desktop\game\text"
data = open(ROM, "rb").read()
N = len(data)

b2c, c2b, controls = {}, {}, {}
for line in open(CHARMAP, encoding="utf-8"):
    line = line.rstrip("\n")
    s = line.strip()
    if s.startswith("@player names") or s.startswith("@japanese"):
        break
    if not s or s.startswith("#") or s.startswith("@"):
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

CTRL_NAMES = {v: k for k, v in controls.items()}
print("charmap:", len(b2c), "controls:", controls)
assert b2c[0x48] == 'a' and b2c[0x2a] == 'A' and b2c[0x02] == ' ', "charmap broken"

def decode(bs):
    out = []
    for b in bs:
        if b in b2c:
            ch = b2c[b]
            out.append("\n" if ch == "\n" else ch)
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

def is_textlike(raw):
    letters = sum(1 for b in raw if 0x2a <= b <= 0x61)
    return letters >= 3

if __name__ == "__main__":
    TABLE_AT, TABLE_N = 0x117dd4, 1792
    story_lo, story_hi = 0x101200, 0x117dd4
    strs = parse_strings(story_lo, story_hi)
    by_off = {off: (ln, raw) for off, ln, raw in strs}
    entries = []
    for k in range(TABLE_N):
        ta = TABLE_AT + 4 * k
        v = int.from_bytes(data[ta:ta+4], "little")
        off = v - 0x08000000
        entries.append((k, ta, off, by_off.get(off)))
    with open(os.path.join(OUT, "dump_story.txt"), "w", encoding="utf-8") as f:
        for k, ta, off, ent in entries:
            if ent:
                ln, raw = ent
                f.write("### %d | tbl=%#x ptr=%#x len=%d\n%s\n" % (k, ta, off, ln, decode(raw)))
            else:
                f.write("### %d | tbl=%#x ptr=%#x MISSING\n" % (k, ta, off))
    lens = [e[3][0] for e in entries if e[3]]
    print("story strings:", len(lens), "max:", max(lens), "avg: %.1f" % (sum(lens)/len(lens)))
    print("\n".join(open(os.path.join(OUT, "dump_story.txt"), encoding="utf-8").read().splitlines()[:40]))
