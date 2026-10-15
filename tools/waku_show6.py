import re

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

starts = []
for i, l in enumerate(lines):
    if l.strip().startswith("THUMB_FUNC_START") or l.strip().startswith("ARM_FUNC_START"):
        starts.append(i)
starts.append(len(lines))

# find function boundaries by label names like sub_80A78F4:
def find_label(name):
    for i, l in enumerate(lines):
        if re.match(r"^" + name + r":", l.strip()):
            return i
    return None

s = find_label("sub_80A78F4")
print("label at", s + 1)
# print until next THUMB_FUNC_START
for i in range(s, len(lines)):
    if i > s and (lines[i].strip().startswith("THUMB_FUNC_START") or lines[i].strip().startswith("ARM_FUNC_START")):
        break
    print(i + 1, lines[i])
