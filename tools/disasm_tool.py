import sys
from capstone import *

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()

def pool_addr(ins, imm):
    return (ins.address + 4) & ~3 | 1 if False else ((ins.address + 4) & ~2) + imm

def disasm_func(start, end):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out = []
    for ins in md.disasm(data[start:end], start):
        extra = ""
        if ins.mnemonic in ("ldr", "ldrb", "ldrh") and "[pc," in ins.op_str:
            # resolve literal
            import re
            m = re.search(r"\[pc, #(0x[0-9a-f]+|\d+)\]", ins.op_str)
            if m:
                imm = int(m.group(1), 0)
                pa = ((ins.address + 4) & ~2) + imm
                val = int.from_bytes(data[pa:pa+4], "little")
                extra = "   ; pool@%#x = %#x (%s)" % (pa, val,
                    ("ptr %#x" % (val - 0x08000000)) if 0x08000000 <= val < 0x08400000 else "")
        if ins.mnemonic == "bl":
            import re
            m = re.search(r"#(0x[0-9a-f]+|\d+)", ins.op_str)
            if m:
                extra = "   ; -> %#x" % int(m.group(1), 0)
        out.append("%#x:\t%s\t%s%s" % (ins.address, ins.mnemonic, ins.op_str, extra))
    return out

if __name__ == "__main__":
    # find function start before pool 0x40f5c: scan back for 'push {..lr}' (b5 xx)
    pool = 0x40f5c
    s = pool
    while s > pool - 0x1000:
        if data[s+1] == 0xB5:
            break
        s -= 2
    print("=== function at %#x ===" % s)
    for line in disasm_func(s, pool + 0x30):
        print(line)
