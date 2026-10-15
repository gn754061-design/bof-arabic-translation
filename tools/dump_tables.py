import json, io, os
master = json.load(open(r"C:\Users\reva4\Desktop\game\text\master.json", encoding="utf-8"))
OUT = r"C:\Users\reva4\Desktop\game\text"

from collections import defaultdict
by_table = defaultdict(list)
for m in master:
    if m["text"]:
        by_table[m["table"]].append(m)

order = sorted(by_table.keys(), key=lambda t: -len(by_table[t]))
for tbl in order:
    rows = by_table[tbl]
    fn = os.path.join(OUT, "table_%08x.txt" % tbl)
    with io.open(fn, "w", encoding="utf-8") as f:
        f.write("### table at %#x : %d entries\n" % (tbl, len(rows)))
        for m in rows:
            f.write("%d\t%#x\t%d\t%s\n" % (m["idx"], m["ptr"], m["len"], m["text"]))
print("wrote", len(order), "table files")
