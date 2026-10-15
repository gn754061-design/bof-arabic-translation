ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

# scan pools in code area 0x5000-0x80000 for values pointing into 0x220000-0x250000
for i in range(0x5000, 0x80000, 4):
    v = int.from_bytes(data[i:i+4], "little")
    if 0x08220000 <= v <= 0x08250000:
        print(f"pool@{i:#x} -> {v - 0x08000000:#x}")
