import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from bof import data, b2c, decode

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK

def quality(raw):
    good = sum(1 for b in raw if b in PRINTABLE)
    bad = sum(1 for b in raw if b not in ALLOWED)
    return good, bad, len(raw)

# walk the story region and sample rejected strings
i = 0x101300
rej = 0
acc = 0
examples = []
while i < 0x105000:
    start = i
    while data[i] != 0x00:
        i += 1
    i += 1
    raw = data[start:i]
    good, bad, ln = quality(raw)
    letters = sum(1 for b in raw if 0x2a <= b <= 0x61)
    if bad > ln * 0.10 or letters < 3 or good / max(1, ln) < 0.8:
        rej += 1
        if len(examples) < 8 and ln > 10:
            examples.append((hex(start), good, bad, ln, decode(raw)[:60]))
    else:
        acc += 1
print("accepted", acc, "rejected", rej)
for e in examples:
    print(e)
