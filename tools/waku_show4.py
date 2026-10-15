import re

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

starts = []
for i, l in enumerate(lines):
    if l.strip().startswith("THUMB_FUNC_START") or l.strip().startswith("ARM_FUNC_START"):
        starts.append(i)
starts.append(len(lines))

def show_func(ln):
    for j in range(len(starts) - 1):
        if starts[j] <= ln - 1 < starts[j + 1]:
            return starts[j], starts[j + 1]
    return None, None

# sub_80A6700 begins around line 4860?
a, b = show_func(4873)
print("func lines", a + 1, b)
for i in range(a, b):
    print(i + 1, lines[i])
