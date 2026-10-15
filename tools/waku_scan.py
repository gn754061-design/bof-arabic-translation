import re

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
print("total lines:", len(lines))
for i, l in enumerate(lines):
    if "gUnknown_082F5AA0" in l or "gUnknown_082F76A0" in l or "gUnknown_08300EA0" in l or "gUnknown_083230" in l:
        print(i + 1, l.strip())
