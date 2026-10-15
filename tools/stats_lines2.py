import json, re
from collections import Counter

master = json.load(open(r"C:\Users\reva4\Desktop\game\text\master.json", encoding="utf-8"))
story = [m for m in master if m["table"] == 0x117dd4 and m["text"]]

def clean_len(line):
    # remove control tokens
    s = re.sub(r"\{[0-9A-Za-z]{2}\}", "", line)
    return len(s)

lens = Counter()
for m in story:
    for line in m["text"].split("{03}"):
        lens[clean_len(line)] += 1
top = sorted(lens.items(), key=lambda x: -x[1])[:20]
print("line length histogram (top):", top)
print("max line len:", max(lens))
print(">=20:", sum(v for k, v in lens.items() if k >= 20), "of", sum(lens.values()))
