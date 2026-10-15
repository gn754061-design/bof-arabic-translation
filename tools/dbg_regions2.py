import sys, os
sys.path.insert(0, os.path.dirname(__file__))
p = os.path.join(os.path.dirname(__file__), "extract_v2.py")
src = open(p, encoding="utf-8").read()
# run everything up to the strings loop
cut = src.index("    strings = {}")
exec(compile(src[:cut], "h", "exec"))
for a, b in regions:
    print("region %#x-%#x (%d)" % (a, b, b - a))
