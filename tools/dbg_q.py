import sys
sys.path.insert(0, r"C:\Users\reva4\Desktop\game\tools")
from bof import data

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CTRL = {0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}

def q(raw):
    good = sum(1 for b in raw if b in PRINTABLE)
    bad = sum(1 for b in raw if b not in PRINTABLE and b not in CTRL)
    return good / len(raw), bad

for off in (0x101238, 0x101281, 0x1012a6, 0x10146f, 0x10156b, 0x102292):
    i = off
    while data[i] != 0:
        i += 1
    raw = data[off:i + 1]
    qq, bad = q(raw)
    print(hex(off), "q=%.3f bad=%d len=%d" % (qq, bad, len(raw)))
