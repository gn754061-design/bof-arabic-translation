ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
N = len(data)

def find_all(pat):
    res = []
    i = data.find(pat)
    while i != -1:
        res.append(i)
        i = data.find(pat, i + 1)
    return res

# distinctive literal pool pattern from sub_80A78F4 pool:
# _080A79A4: .4byte 0x06010200
# _080A79A8: .4byte <font base>
# _080A79AC: .4byte 0x040000D4
# _080A79B0: .4byte 0x80000010
p1 = (0x06010200).to_bytes(4, "little")
p2 = (0x040000D4).to_bytes(4, "little")
p3 = (0x80000010).to_bytes(4, "little")

for i in find_all(p1):
    window = data[i - 16:i + 24]
    words = [int.from_bytes(data[j:j+4], "little") for j in range(i - 16, i + 24, 4)]
    print(f"0x06010200 at {i:#x}: window words = {[hex(w) for w in words]}")

print()
for i in find_all(p3)[:20]:
    print(f"0x80000010 at {i:#x}: prev words = {[hex(int.from_bytes(data[j:j+4],'little')) for j in range(i-12, i, 4)]}")
