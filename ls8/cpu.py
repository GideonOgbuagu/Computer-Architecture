"""CPU functionality."""

import sys

HLT = 0b00000001 
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
CMP = 0b10100111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        pass
        self.ram = [0] * 256

        self.registers = [0] * 8

        self.registers[7] = 0xF4

        self.pc = 0

        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,

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
                        continue # skip to next iteration of loop

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
        #elif op == "SUB": etc
        # elif op == CMP:
            

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
        
                

# Minimum Viable Product
# Your finished project must include all of the following requirements:

#  Add the CMP instruction and equal flag to your LS-8.

#  Add the JMP instruction.

#  Add the JEQ and JNE instructions.