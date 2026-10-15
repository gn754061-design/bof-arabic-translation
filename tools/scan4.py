import sys, collections, re

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

DELTA = 0x19

def dec(bs):
    out = []
    for b in bs:
        c = b + DELTA
        out.append(chr(c) if 0x20 <= c < 0x7f else "\x00")
    return "".join(out)

# find all runs of "letter bytes" (b in 0x2a..0x61 approx => printable) separated by other bytes
runs = []
i = 0
n = len(data)
cur = bytearray()
start = 0
for i in range(n):
    b = data[i]
    if 0x2a <= b <= 0x61:
        if not cur:
            start = i
        cur.append(b)
    else:
        if len(cur) >= 4:
            runs.append((start, bytes(cur)))
        cur = bytearray()

print("runs:", len(runs))
# where are runs concentrated?
by_bank = collections.Counter()
for off, r in runs:
    by_bank[off >> 16] += 1
print("runs per 64KB:", sorted(by_bank.items()))

# print a few sample runs from the densest region
densest = [b for b, _ in by_bank.most_common(3)]
for off, r in runs:
    if (off >> 16) in densest:
        print(hex(off), dec(r))
