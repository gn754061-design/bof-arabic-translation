import sys
from capstone import *
from capstone.arm import *

ROM = r"C:\Users\reva4\Desktop\game\rom\bof_usa.gba"
data = open(ROM, "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

def show(start, length, label=""):
    print("=== %s %#x ===" % (label, start))
    for ins in md.disasm(data[start:start+length], start):
        extra = ""
        for op in ins.operands:
            if op.type == ARM_OP_MEM and op.mem.base == ARM_REG_PC:
                pa = ((ins.address + 4) & ~2) + op.mem.disp
                val = int.from_bytes(data[pa:pa+4], "little")
                if 0x08000000 <= val < 0x08400000:
                    extra = "   ; -> ptr %#x" % (val - 0x08000000)
                else:
                    extra = "   ; = %#x" % val
            if op.type == ARM_OP_IMM and ins.mnemonic in ("bl", "blx"):
                extra = "   ; -> %#x" % op.imm
        print("%#x:\t%s\t%s%s" % (ins.address, ins.mnemonic, ins.op_str, extra))

if __name__ == "__main__":
    show(0x5ade4, 0x130, "glyph path 0x5ade4")
