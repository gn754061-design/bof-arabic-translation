import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "font"))
from arabic_encode import encode_marked
sys.path.insert(0, r"C:\Users\reva4\Desktop\game\tools")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.insert import load_translations, encode_template

trans = load_translations()
master = json.load(open(r"C:\Users\reva4\Desktop\game\text\entries.json", encoding="utf-8"))
known = {m["ptr"]: m for m in master if m["text"]}

for ptr in sorted(trans):
    b = encode_template(trans[ptr])
    ent = known.get(ptr)
    if ent:
        slot = ent["len"]
        refs = ent.get("refs", [])
    else:
        rom = open(r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba", "rb").read()
        i = ptr
        while rom[i] != 0:
            i += 1
        slot = (i - ptr) + 1
        import re
        pat = (0x08000000 + ptr).to_bytes(4, "little")
        refs = []
        j = rom.find(pat)
        while j != -1:
            refs.append(j)
            j = rom.find(pat, j + 1)
    if len(b) + 1 > slot and not refs:
        print("NOREF %#x len=%d slot=%d refs=%d text=%r" % (ptr, len(b), slot, len(refs), trans[ptr][:50]))
