"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.running = True
        self.pc = 0
        self.ir = 0x00
        self.instructions = {
            "HLT": 0x01,
            "LDI": 0x82,
            "PRN": 0x47
        }
        self.branch_table = {
            0x01: self.hlt,
            0x82: self.ldi,
            0x47: self.prn,
            0xA2: self.mul
        }

    def mul(self, a, b):
        self.alu('MUL', a, b)
        self.pc = self.pc + 3
        
    def add(self, a, b):
        self.alu('ADD', a, b)
        
    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, addr, val):
        self.ram[addr] = val

    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]
        with open(filename) as f:
            address = 0
            for line in f:
                line = line.split('#')
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                self.ram_write(address, v)
                address += 1

    def hlt(self):
        sys.exit(1)
        self.pc = self.pc + 1

    def ldi(self, reg, i):
        self.reg[reg] = i
        self.pc = self.pc + 3

    def prn(self, reg, b=None):
        print(self.reg[reg])
        self.pc = self.pc + 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        while self.running:
            self.ir = self.ram_read(self.pc)
            if self.ir == self.instructions['HLT']:
                self.hlt()
                break
            a = self.ram_read(self.pc + 1)
            b = self.ram_read(self.pc + 2)
            self.branch_table[self.ir](a, b)
