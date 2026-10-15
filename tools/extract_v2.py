# -*- coding: utf-8 -*-
"""Definitive extractor: strings + reference map for the BoF (USA) GBA ROM."""
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
    good = sum(1 for b in raw if b in PRINTABLE)
    bad = sum(1 for b in raw if b not in ALLOWED)
    if bad > len(raw) * 0.12:
        return 0.0
    if sum(1 for b in raw if 0x2a <= b <= 0x61) < 3:
        return 0.0
    return good / len(raw)

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

    strings = {}
    for a, b in regions:
        for off, ln, raw in parse_strings(a, b):
            q = quality(raw)
            if q >= 0.85:
                strings[off] = {"len": ln, "text": decode(raw), "q": round(q, 3)}
    print("regions:", len(regions), "strings:", len(strings))

    # reference map: every 4-byte aligned pointer that targets a string start
    starts = set(strings.keys())
    refs = {}
    for i in range(0, N - 4, 4):
        v = int.from_bytes(data[i:i+4], "little")
        off = v - 0x08000000
        if off in starts:
            refs.setdefault(off, []).append(i)
    print("referenced strings:", len(refs), "total refs:", sum(len(v) for v in refs.values()))

    # entries = strings that are referenced
    entries = []
    for off in sorted(refs):
        s = strings[off]
        entries.append({"ptr": off, "len": s["len"], "text": s["text"], "q": s["q"],
                        "refs": refs[off]})
    json.dump(entries, open(os.path.join(OUT, "entries.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("entries:", len(entries), "text bytes:", sum(e["len"] for e in entries))

    # per-entry dump for translators (grouped by region)
    from collections import defaultdict
    byblock = defaultdict(list)
    for e in entries:
        byblock[e["ptr"] >> 16].append(e)
    os.makedirs(os.path.join(OUT, "en"), exist_ok=True)
    for blk, es in sorted(byblock.items()):
        with open(os.path.join(OUT, "en", "block_%02x.txt" % blk), "w", encoding="utf-8") as f:
            for e in es:
                f.write("%#x\t%d\t%s\n" % (e["ptr"], e["len"], e["text"]))
    print("wrote", len(byblock), "block files")

if __name__ == "__main__":
    main()
