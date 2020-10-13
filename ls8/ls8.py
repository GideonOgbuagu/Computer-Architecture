#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
print("hello")
# TODO: grab any args
if len(sys.argv) != 2:
    print("usage: simple.py filename")
    sys.exit(1)
# TODO: load opcodes in to memory
print(sys.argv)
cpu.load(sys.argv[1])

cpu.run()