#!/usr/bin/env python3

HELP = '''
This simple script replays the commands logged by 
the EggBot Inkscape extension.

Usage: python3 ebb_replay_log.py <logfile> <serial port>
'''

from serial import Serial
import sys

if len(sys.argv) < 3:
    print(HELP)
    sys.exit(-1)

filename = sys.argv[1]
port = sys.argv[2]

ser = Serial(port, 115200)
commands = open(filename).readlines()

for command in commands:
    ser.write(command.encode('ascii'))
    ret = ser.readline()
    print(command, ret)
