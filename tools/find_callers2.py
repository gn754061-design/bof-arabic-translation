import re

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

starts = []
for i, l in enumerate(lines):
    if l.strip().startswith("THUMB_FUNC_START") or l.strip().startswith("ARM_FUNC_START"):
        starts.append(i)
starts.append(len(lines))

# function that contains line 7349 (index 7348)
target = None
for j in range(len(starts) - 1):
    if starts[j] <= 7348 < starts[j + 1]:
        target = starts[j]
print("caller func starts at line", target + 1)
print(lines[target].strip())

# who calls it? print header lines around each function start to get its name symbol
# find 'bl <name>' referencing the function's label: capture label from THUMB_FUNC_START line
name = lines[target].split()[1]
print("name:", name)
for i, l in enumerate(lines):
    if re.search(r"bl\s+" + name + r"\b", l):
        print("called from line", i + 1, "in file waku.s")
