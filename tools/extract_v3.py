# -*- coding: utf-8 -*-
"""Definitive entry list: strings referenced by code-referenced (live) pointer tables."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bof import data, N, b2c, controls, decode

PRINTABLE = set([0x02]) | set(range(0x20, 0x7e)) | set(range(0xef, 0xf6))
CONTROL_OK = {0x00, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d}
ALLOWED = PRINTABLE | CONTROL_OK
OUT = r"C:\Users\reva4\Desktop\game\text"

def quality(raw):
    if len(raw) < 4:
        return 0.0
    if sum(1 for b in raw if 0x2a <= b <= 0x61) < 3:
        return 0.0
    bad = sum(1 for b in raw if b not in ALLOWED)
    if bad > len(raw) * 0.15:
        return 0.0
    return sum(1 for b in raw if b in PRINTABLE) / len(raw)

def parse_strings(a, b):
    res, i = [], a
    while i < b:
        start = i
        while i < b and data[i] != 0x00:
            i += 1
        if i < b:
            i += 1
        res.append((start, i - start, data[start:i]))
        if i >= b:
            break
    return res

def main():
    # 1. text regions (loose)
    BLK = 256
    scores = [(off, sum(1 for b in data[off:off + BLK] if b in ALLOWED) / BLK)
              for off in range(0, N, BLK)]
    regions, cur_start, cur = [], None, []
    for off, sc in scores:
        if sc >= 0.7:
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
    # explicit region: the game's main text bank (story + menus + names)
    regions.append((0x100000, 0x152000))

    def in_regions(off):
        return any(a <= off < b for a, b in regions)

    # 2. all strings in regions
    strings = {}
    for a, b in regions:
        for off, ln, raw in parse_strings(a, b):
            q = quality(raw)
            if q >= 0.6:
                strings[off] = (ln, raw, q)

    # 3. code-referenced targets
    code_refs = set()
    for i in range(0, N - 4, 4):
        v = int.from_bytes(data[i:i + 4], "little")
        if 0x08000000 <= v < 0x08000000 + N:
            code_refs.add(v - 0x08000000)

    # 4. positions holding a pointer into a region
    is_ptr = {}
    for i in range(0, N - 4, 4):
        v = int.from_bytes(data[i:i + 4], "little")
        off = v - 0x08000000
        if in_regions(off):
            is_ptr[i] = off

    # 5. seed = code-referenced position near region pointers
    seeds = set()
    for p in code_refs:
        for d in (-8, -4, 0, 4, 8):
            if (p + d) in is_ptr:
                seeds.add(p + d)
                break

    # 6. expand runs
    def expand(s):
        a = s
        while (a - 4) in is_ptr:
            a -= 4
        b, gap = s, 0
        while b + 4 < N - 4 and gap <= 24:
            nxt = b + 4
            if nxt in is_ptr:
                b, gap = nxt, 0
            else:
                gap += 4
                if gap > 24:
                    break
                b = nxt
        return a, b

    spans = {}
    for s in seeds:
        a, b = expand(s)
        if a not in spans or b - a > spans[a][1] - spans[a][0]:
            spans[a] = (a, b)

    live_tables = []
    for key, (a, b) in sorted(spans.items()):
        run = [(i, is_ptr[i]) for i in range(a, b + 1, 4) if i in is_ptr]
        good = sum(1 for _, off in run if off in strings and strings[off][2] >= 0.7)
        if good / len(run) >= 0.5:
            live_tables.append(run)

    print("live tables:", len(live_tables))
    for t in sorted(live_tables, key=lambda x: -len(x)):
        print("  %#x: %d entries" % (t[0][0], len(t)))

    # 7. entries = union of live-table entries pointing at strings
    seen = {}
    for t in live_tables:
        for ta, off in t:
            if off in strings and off not in seen:
                ln, raw, q = strings[off]
                seen[off] = {"ptr": off, "len": ln, "text": decode(raw), "q": round(q, 3)}

    # 8. reference map for relocation
    refs = {}
    for i in range(0, N - 4, 4):
        v = int.from_bytes(data[i:i + 4], "little")
        off = v - 0x08000000
        if off in seen:
            refs.setdefault(off, []).append(i)

    entries = []
    for off in sorted(seen):
        e = seen[off]
        e["refs"] = refs.get(off, [])
        entries.append(e)
    json.dump(entries, open(os.path.join(OUT, "entries.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    print("entries:", len(entries), "bytes:", sum(e["len"] for e in entries))

if __name__ == "__main__":
    main()
