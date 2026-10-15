p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
for i in range(12960, 13100):
    print(i + 1, lines[i])
