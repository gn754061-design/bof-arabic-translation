import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
exec(open(os.path.join(os.path.dirname(__file__), "extract_final.py"), encoding="utf-8").read().split("# --- pointers")[0])

print("0x101238 in strings:", 0x101238 in strings)
print("0x101281 in strings:", 0x101281 in strings)
# check table area
for i in range(0x117dd4, 0x117dd4 + 40, 4):
    v = int.from_bytes(data[i:i+4], "little")
    off = v - 0x08000000
    print(hex(i), hex(v), "in_regions:", in_regions(off), "in_strings:", off in strings,
          "q:", round(strings.get(off, (0, b"", 0))[2], 2) if off in strings else "-")
