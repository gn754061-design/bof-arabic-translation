ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def show(off, n=160):
    chunk = data[off:off+n]
    print(hex(off))
    print(chunk[:n//2].hex(" "))
    print(chunk[n//2:].hex(" "))
    print(repr(chunk))

show(0x101a86 - 64, 256)
print("=" * 60)
show(0x10161e - 64, 256)
