import sys
sys.path.insert(0, r"C:\Users\reva4\Desktop\game\tools")
from bof import data, N

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK

BLK = 256
scores = []
for off in range(0, N, BLK):
    chunk = data[off:off + BLK]
    scores.append((off, sum(1 for b in chunk if b in ALLOWED) / len(chunk)))
regions, cur_start, cur = [], None, []
for off, sc in scores:
    if sc >= 0.75:
        if cur_start is None:
            cur_start = off
        cur.append(off)
    else:
        if cur_start is not None and len(cur) >= 4:
            regions.append((cur_start, cur[-1] + BLK))
        cur_start, cur = None, []
if cur_start is not None and len(cur) >= 4:
    regions.append((cur_start, cur[-1] + BLK))
regions = [(max(0, a - BLK), min(N, b + BLK)) for a, b in regions if b - a >= 512 and a < 0x318000]
for a, b in sorted(regions, key=lambda r: -(r[1] - r[0]))[:30]:
    print("region %#x-%#x (%d)" % (a, b, b - a))
