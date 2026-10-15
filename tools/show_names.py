import json
master = json.load(open(r"C:\Users\reva4\Desktop\game\text\master.json", encoding="utf-8"))

# short-string tables
for tbl in (0x14ff50, 0x14f530, 0x14e47c, 0x14f9d0, 0x150468, 0x14ed84, 0x14f138, 0xfdd4c):
    rows = [m for m in master if m["table"] == tbl and m["text"]]
    print("=== table %#x: %d entries" % (tbl, len(rows)))
    for m in rows[:12]:
        print("   ", repr(m["text"])[:70], "len", m["len"])
