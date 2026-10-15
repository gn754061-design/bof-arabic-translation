ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

def valid2(b):
    return all(((x & 0xF) in (0, 1)) and ((x >> 4) in (0, 1)) for x in b)

runs = []
i = 0
while i + 32 <= N:
    j = i
    cnt = 0
    while j + 32 <= N and valid2(data[j:j+32]):
        cnt += 1
        j += 32
    if cnt >= 8:
        runs.append((i, cnt))
        i = j
    else:
        i += 32
runs.sort(key=lambda x: -x[1])
for off, cnt in runs[:25]:
    print(f"{off:#x} tiles={cnt} bytes={cnt*32:#x}")
