"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
PSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001

CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

EFLAG = 0b001
LFLAG = 0b011
GFLAG = 0b0


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        pass
        self.ram = [0] * 256

        self.registers = [0] * 8

        # self.registers[7] = 0xF4

        self.pc = 0

        self.flag = None

        self.stack_pointer = 0xf4
        self.registers[7] = self.stack_pointer

        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            ADD: self.add,
            PSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,
            CMP: self.cmp,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne

        }

    def load(self):
        """Load a program into memory."""

        # For now, we've just hardcoded a program:
        if (len(sys.argv)) != 2:
            print("remember to pass the second file name")
            print("usage: python3 fileio.py <second_file_name.py>")
            sys.exit()

        address = 0
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    # parse the file to isolate the binary opcodes
                    possible_number = line[:line.find('#')]
                    if possible_number == '':
                        continue  # skip to next iteration of loop

                    instruction = int(possible_number, 2)

                    self.ram[address] = instruction

                    address += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            sys.exit()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == MUL:
            self.registers[reg_a] *= self.registers[reg_b]
        # elif op == "SUB": etc
        elif op == CMP:
            a = self.registers[reg_a]
            b = self.registers[reg_b]
            if a > b:
                self.flag = GFLAG
            elif a < b:
                self.flag = LFLAG
            else:
                self.flag = EFLAG

        elif op == 'AND':
            self.registers[reg_a] = self.registers[reg_a] & self.registers[reg_b]
        elif op == 'OR':
            self.registers[reg_a] = self.registers[reg_a] | self.registers[reg_b]
        elif op == 'XOR':
            self.registers[reg_a] = self.registers[reg_a] ^ self.registers[reg_b]
        elif op == 'NOT':
            self.registers[reg_a] = ~self.registers[reg_a]
        elif op == 'SHL':
            self.registers[reg_a] = self.registers[reg_a] << self.registers[reg_b]
        elif op == 'SHR':
            self.registers[reg_a] = self.registers[reg_a] >> self.registers[reg_b]
        elif op == 'MOD':
            self.registers[reg_a] = self.registers[reg_a] % self.registers[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            num_operands = IR >> 6
            self.pc += 1 + num_operands

            is_alu_op = ((IR >> 5) & 0b001) == 1

            if is_alu_op:
                self.alu(IR, operand_a, operand_b)

            else:
                self.branchtable[IR](operand_a, operand_b)

    def hlt(self, operand_a, operand_b):
        self.running = False

    def ldi(self, operand_a, operand_b):
        self.registers[operand_a] = operand_b

    def prn(self, operand_a, operand_b):
        print(self.registers[operand_a])

    def push(self, a, b=None):
        # decrement stack pointer
        self.stack_pointer -= 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF
        # get register number and value stored at specified reg number
        reg_num = self.ram[self.pc + 1]
        val = self.registers[reg_num]
        # store value in ram
        self.ram[self.stack_pointer] = val
        self.pc += 2

    def pop(self, a, b=None):
        # get value from RAM
        val = self.ram[self.stack_pointer]
        # store at given register
        reg_num = self.ram[self.pc + 1]
        self.registers[reg_num] = val
        # increment stack pointer and program counter
        self.stack_pointer += 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF
        self.pc += 2

    def call(self, a, b):
        # return counter, save to stack
        rc = self.pc + 2
        self.stack_pointer -= 1
        self.ram[self.stack_pointer] = rc
        self.pc = self.registers[a]

    def ret(self, a, b):
        # pop from stack
        val = self.ram[self.stack_pointer]
        # set pc back to previous
        self.pc = val
        # increment stack pointer
        self.stack_pointer += 1

    def add(self, a, b):
        self.alu('ADD', a, b)
        self.pc += 3

    def cmp(self, operand_a, operand_b):
        self.alu('CMP', operand_a, operand_b)
        self.pc += 3

    def jeq(self, operand_a, operand_b):
        if self.flag == EFLAG:
            self.pc = self.registers[operand_a]
        else:
            self.pc += 2

    def jne(self, operand_a, operand_b):
        if self.flag != EFLAG:
            self.pc = self.registers[operand_a]
        else:
            self.pc += 2

    def jmp(self, operand_a, operand_b):
        self.pc = self.registers[operand_a]
