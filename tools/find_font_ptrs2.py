ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

lo, hi = 0x0822E000, 0x08236000
hits = []
for i in range(0, N - 4, 4):
    v = int.from_bytes(data[i:i+4], "little")
    if lo <= v < hi:
        hits.append((i, v - 0x08000000))
print(len(hits))
for i, off in hits[:60]:
    print(f"  ptr_at={i:#x} -> {off:#x}")
