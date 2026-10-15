import sys, os
sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(__file__), "extract_final.py"), encoding="utf-8").read()
head = src.split("# --- pointers")[0]
exec(compile(head, "head", "exec"))

TABLE = 0x117dd4
missing = []
present = 0
for k in range(1792):
    ta = TABLE + 4 * k
    v = int.from_bytes(data[ta:ta+4], "little")
    off = v - 0x08000000
    if off in strings:
        present += 1
    else:
        missing.append((k, hex(ta), hex(off)))
print("present:", present, "missing:", len(missing))
for m in missing[:15]:
    print(m)
# check a missing target
if missing:
    k, ta, off = missing[0]
    off = int(off, 16)
    i = off
    while i < 0x118000 and data[i] != 0:
        i += 1
    raw = data[off:i+1]
    from bof import decode
    print("missing string at", hex(off), "len", len(raw))
    print(repr(decode(raw)[:120]))
