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
        self.reg[7] = 0xf4
        self.reg[6] = 0b00000000
        self.sp = self.reg[7]
        self.fl = self.reg[6]

        self.instructions = {
            "HLT": 0x01,
            "LDI": 0x82,
            "PRN": 0x47
        }
        self.branch_table = {
            0x01: self.hlt,
            0x82: self.ldi,
            0x47: self.prn,
            0xA2: self.mul,
            0x46: self.pop,
            0x45: self.push,
            0x50: self.call,
            0x11: self.ret,
            0x54: self.jmp,
            0x55: self.jeq,
            0xA7: self.cmpr,
            0b10100000: self.add
        }

    # def add(self, a, b):
    #     self.alu("ADD", a, b)
    #     self.pc += 3
    def cmpr(self, a, b):
        self.alu('CMP', a, b)
        self.pc = self.pc + 3

    def jeq(self, reg_index):
        if self.fl == 0b00000001:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 1

    def jmp(self, reg_index):
        self.pc = self.reg[reg_index]

    def ret(self):
        # Ret pops the return_addr off the stack, and sets self.pc to it
        # reference return addr to set pc to it
        return_addr = self.ram_read(self.sp)
        self.pc = return_addr  # set pc to return addr, so that next subroutine is executed
        self.sp += 1  # Increment sp since we are poping stack

    def call(self, a=None):
        # The call instruction places the address of where we will be after this call is returned
        # onto the stack. It then makes the program counter point to the current subroutine
        return_addr = self.pc + 2

        self.sp -= 1  # Decrement sp to grow stack
        # place return address on top of stack
        self.ram_write(self.sp, return_addr)

        # The instruction set comes with the register that contains addr of current subr
        reg_index = self.ram_read(self.pc + 1)
        subr_addr = self.reg[reg_index]  # Reference that address

        # This happens instead of incrementing, since instruction set contained subr addr
        self.pc = subr_addr

    def push(self, a):
        # Decrement sp, add value at new position in memory
        self.sp -= 1
        reg_index = self.ram_read(self.pc+1)
        value = self.reg[reg_index]
        self.ram_write(self.sp, value)
        self.pc += 2

    def pop(self, a=None):
        value = self.ram_read(self.sp)
        reg_index = self.ram_read(self.pc + 1)
        self.reg[reg_index] = value
        self.sp += 1
        self.pc += 2

    def mul(self, a, b):
        self.alu('MUL', a, b)
        self.pc = self.pc + 3

    def add(self, a, b):
        self.alu('ADD', a, b)
        self.pc += 3

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
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if reg_a > reg_b:
                self.fl = 0b00000010
            elif reg_a == reg_b:
                self.fl = 0b00000001
            elif reg_a < reg_b:
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation", op)

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
                return

            a = self.ram_read(self.pc + 1)
            b = self.ram_read(self.pc + 2)

            params = self.ir >> 6
            if self.ir in self.branch_table:
                print('Good IR', self.ir)
                if params == 0:
                    self.branch_table[self.ir]()
                elif params == 1:
                    self.branch_table[self.ir](a)
                else:
                    self.branch_table[self.ir](a, b)
            else:
                print("Bad IR", self.ir)
                pass
