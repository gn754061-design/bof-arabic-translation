import json, re
from collections import Counter

master = json.load(open(r"C:\Users\reva4\Desktop\game\text\master.json", encoding="utf-8"))
story = [m for m in master if m["table"] == 0x117dd4 and m["text"]]

lens = Counter()
alllines = []
for m in story:
    t = m["text"]
    # split on \n (03) rendered as actual newline in decode
    for line in t.split("\n"):
        alllines.append(len(line))
        lens[len(line)] += 1

top = sorted(lens.items(), key=lambda x: -x[1])[:15]
print("most common line lengths:", top)
print("max:", max(alllines), "count of lines>=20:", sum(1 for l in alllines if l >= 20))

# check control args: count occurrences of {ITEM}/{WEAPON}/{DEFENSE}/{STRING} etc.
ctrl = Counter()
for m in story:
    for c in re.findall(r"\{(\w+)\}", m["text"]):
        ctrl[c] += 1
print("controls:", ctrl)

# check F7 usage
print("F7 count:", sum(m["text"].count("{F7}") for m in story))
