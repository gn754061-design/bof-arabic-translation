ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

# find runs of 32-byte tiles whose nibbles are all in {0,1} (2-level font) or {0,3}
best = []
i = 0
while i < N - 32:
    run = 0
    j = i
    while j + 32 <= N:
        chunk = data[j:j+32]
        ok = True
        for b in chunk:
            lo, hi = b & 0xF, b >> 4
            if not ((lo in (0, 1) and hi in (0, 1)) or (lo in (0, 3) and hi in (0, 3))):
                ok = False
                break
        if not ok:
            break
        run += 1
        j += 32
    if run >= 24:
        best.append((i, run))
        i = j
    else:
        i += 32 if run == 0 else j

best.sort(key=lambda x: -x[1])
for off, run in best[:20]:
    print(f"offset {off:#x} tiles={run} bytes={run*32:#x}")
