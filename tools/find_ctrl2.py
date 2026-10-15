import re

p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

funcs = []
cur = None
for i, l in enumerate(lines):
    m = re.match(r"(?:THUMB_FUNC_START|ARM_FUNC_START)\s+(\S+)", l.strip())
    if m:
        cur = (m.group(1), i + 1)
    if re.search(r"cmp\s+r\d+,\s*#0x(?:[1-9a-d])\b", l) or re.search(r"cmp\s+r\d+,\s*#(?:[1-9]|1[0-3])\b", l):
        funcs.append((cur[0] if cur else "?", i + 1, l.strip()))

for f in funcs[:80]:
    print(f)
