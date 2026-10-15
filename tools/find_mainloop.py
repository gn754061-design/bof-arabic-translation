import re

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

starts = []
for i, l in enumerate(lines):
    if l.strip().startswith("THUMB_FUNC_START") or l.strip().startswith("ARM_FUNC_START"):
        starts.append(i)
starts.append(len(lines))

def func_of(ln):
    for j in range(len(starts) - 1):
        if starts[j] <= ln - 1 < starts[j + 1]:
            return starts[j] + 1
    return None

pat = re.compile(r"cmp\s+r\d+,\s*#0x(?:20|1f|7f|80|0f|10|11|12|13)\b")
seen = set()
for i, l in enumerate(lines):
    if pat.search(l):
        fo = func_of(i + 1)
        if fo and fo not in seen:
            seen.add(fo)
            print(f"func@{fo}: {l.strip()}  (line {i+1})")
