import re, glob

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

# find function start/end ranges
starts = []
for i, l in enumerate(lines):
    if l.strip().startswith("THUMB_FUNC_START") or l.strip().startswith("ARM_FUNC_START"):
        starts.append(i)
starts.append(len(lines))

def func_of(ln):
    for j in range(len(starts) - 1):
        if starts[j] <= ln < starts[j + 1]:
            return starts[j]
    return None

# callers of sub_80A78F4
callers = {}
for i, l in enumerate(lines):
    if re.search(r"bl\s+sub_80A78F4\b", l) or re.search(r"bl\s+sub_80A78F4\s", l):
        fs = func_of(i)
        callers.setdefault(fs, []).append(i + 1)

for fs, lns in callers.items():
    # print function header name
    for k in range(fs, fs + 3):
        pass
    print("func at line", fs + 1, "calls at", lns[:10], "count", len(lns))
    # show first line of function
    print("   ", lines[fs].strip()[:100])
