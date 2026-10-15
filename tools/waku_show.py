p = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm\waku.s"
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()

def show(a, b):
    for i in range(a - 1, min(b, len(lines))):
        print(i + 1, lines[i])

# context around the printing routine near line 7345 (small font use)
show(7280, 7420)
