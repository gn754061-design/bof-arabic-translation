import re, glob, os

base = r"C:\Users\reva4\Desktop\game\ref\bof_disasm\asm"
targets = ["sub_80A78F4", "sub_80A79B4", "sub_80A79FC"]
res = {t: [] for t in targets}
for f in glob.glob(os.path.join(base, "*.s")):
    for i, l in enumerate(open(f, encoding="utf-8", errors="replace")):
        for t in targets:
            if re.search(r"bl\s+" + t + r"\b", l):
                res[t].append((os.path.basename(f), i + 1, l.strip()))
for t, v in res.items():
    print("== callers of", t, len(v))
    for x in v[:20]:
        print("   ", x)
