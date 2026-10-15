# -*- coding: utf-8 -*-
"""
Insert Arabic translations into the BoF (USA) GBA ROM.

Rules:
  * strings that fit their original slot are written in place
  * longer strings are appended to an overflow area at 0x400000 (ROM expanded)
    and every pointer to the original string is repatched
"""
import json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "font"))
from arabic_encode import encode_marked, BASIC

ROM_IN = os.environ.get("BOF_ROM", r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba")
ROM_OUT = r"C:\Users\reva4\Desktop\game\build\bof_arabic.gba"
MASTER = r"C:\Users\reva4\Desktop\game\text\entries.json"
TRANS_DIR = r"C:\Users\reva4\Desktop\game\text\arabic"

OVERFLOW = 0x400000

TOKEN_BYTES = {
    "END": 0x00, "NEW": 0x09, "COLOR": 0x04, "PLAYER": 0x05,
    "NAME": 0x06, "ITEM": 0x0B, "WEAPON": 0x0C, "DEFENSE": 0x0D,
    "STRING": 0x0A, "KANJI": 0x01, "CODE7": 0x07, "CODE8": 0x08,
    "03": 0x03,
}

def encode_template(text):
    """Template string -> bytes (without terminator)."""
    codes = encode_marked(text)
    out = bytearray()
    for c in codes:
        if isinstance(c, str):
            m = re.fullmatch(r"\{(\w+)\}", c)
            if not m:
                raise ValueError("bad token %r" % c)
            name = m.group(1)
            if name in TOKEN_BYTES:
                out.append(TOKEN_BYTES[name])
            elif re.fullmatch(r"[0-9A-Fa-f]{2}", name):
                out.append(int(name, 16))
            else:
                raise ValueError("unknown token %r" % c)
        else:
            out.append(c)
    return bytes(out)

def load_translations():
    trans = {}
    for fn in sorted(os.listdir(TRANS_DIR)):
        if not fn.endswith(".txt"):
            continue
        for line in open(os.path.join(TRANS_DIR, fn), encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            ptr, _, txt = line.partition("\t")
            trans[int(ptr, 16)] = txt
    return trans

def main():
    master = json.load(open(MASTER, encoding="utf-8"))
    rom = open(ROM_IN, "rb").read()
    data = bytearray(rom)
    if len(data) < OVERFLOW + 0x40000:
        data.extend(b"\xff" * (OVERFLOW + 0x40000 - len(data)))
    ov = OVERFLOW

    # index known entries
    known = {}
    for m in master:
        if m["text"] is not None and m["len"] > 0:
            known[m["ptr"]] = m

    # build pointer map: string-start offset -> [ref positions]
    starts = set(known.keys())
    refs = {}
    for m in master:
        if m["text"] is not None and m["len"] > 0:
            for rp in m.get("refs", []):
                refs.setdefault(m["ptr"], []).append(rp)

    trans = load_translations()
    print("translations loaded:", len(trans))

    # for addresses not in the index, measure the original slot from the ROM
    slot_of = {}
    for ptr in trans:
        if ptr in known:
            slot_of[ptr] = known[ptr]["len"]
        else:
            i = ptr
            while i < len(rom) and rom[i] != 0x00:
                i += 1
            slot_of[ptr] = (i - ptr) + 1
            # find refs by scanning
            pat = (0x08000000 + ptr).to_bytes(4, "little")
            pos = []
            j = rom.find(pat)
            while j != -1 and j < OVERFLOW:
                pos.append(j)
                j = rom.find(pat, j + 1)
            refs[ptr] = pos

    stats = {"inplace": 0, "relocated": 0, "skipped": 0, "noref": 0}
    reloc = {}
    log = []
    for ptr in sorted(trans):
        txt = trans[ptr]
        if ptr in known and known[ptr].get("text") is None:
            continue
        try:
            b = encode_template(txt)
        except Exception as e:
            stats["skipped"] += 1
            log.append("ENCFAIL %#x: %s | %s" % (ptr, e, txt[:40]))
            continue
        slot = slot_of[ptr]
        if len(b) + 1 <= slot:
            data[ptr:ptr + len(b) + 1] = b + b"\x00"
            stats["inplace"] += 1
        else:
            data[ov:ov + len(b) + 1] = b + b"\x00"
            for rp in refs.get(ptr, []):
                data[rp:rp + 4] = (0x08000000 + ov).to_bytes(4, "little")
            if not refs.get(ptr):
                stats["noref"] += 1
            reloc["%#x" % ptr] = "%#x" % ov
            stats["relocated"] += 1
            ov += (len(b) + 2) & ~1
    print(stats)
    print("overflow used: %#x bytes" % (ov - OVERFLOW))
    for l in log[:20]:
        print(l)
    json.dump(reloc, open(r"C:\Users\reva4\Desktop\game\build\reloc.json", "w", encoding="utf-8"))
    open(ROM_OUT, "wb").write(bytes(data))
    print("wrote", ROM_OUT)

if __name__ == "__main__":
    main()
