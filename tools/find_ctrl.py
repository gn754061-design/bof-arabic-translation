import glob, re, os

base = r"C:\Users\reva4\Desktop\game\ref\bof_disasm"
pats = [r"cmp r\d+, #0xd\b", r"cmp r\d+, #0x0d\b", r"cmp r\d+, #0xb\b", r"cmp r\d+, #0x9\b", r"cmp r\d+, #0x3\b", r"cmp r\d+, #0x6\b", r"cmp r\d+, #0xa\b"]
hits = []
for f in glob.glob(os.path.join(base, "asm", "*.s")) + glob.glob(os.path.join(base, "src", "**", "*.c"), recursive=True):
    try:
        txt = open(f, encoding="utf-8", errors="replace").read().splitlines()
    except Exception:
        continue
    for i, l in enumerate(txt):
        for p in pats:
            if re.search(p, l):
                hits.append((os.path.basename(f), i + 1, l.strip()))
                break
for h in hits[:60]:
    print(h)
