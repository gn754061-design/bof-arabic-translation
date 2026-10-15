import sys, os
sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(__file__), "extract_strict.py"), encoding="utf-8").read()
src = src.split('# keep tables where')[0]
src = src.replace('regions, cur_start, cur = [], None, []', 'regions, cur_start, cur = [], None, []')
exec(compile(src, "dbg", "exec"))
for a, b in regions:
    if b - a >= 2048:
        print("  region %#x-%#x (%d bytes)" % (a, b, b - a))
print("strings:", len(all_strings))
