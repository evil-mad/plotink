# coding=utf-8
# ebb_serial.py
# Serial connection utilities for EiBotBoard
# https://github.com/evil-mad/plotink
# 
# Intended to provide some common interfaces that can be used by 
# EggBot, WaterColorBot, AxiDraw, and similar machines.
#
# Version 0.9, Dated March 5, 2018.
#
# Thanks to Shel Michaels for bug fixes and helpful suggestions. 
#
# The MIT License (MIT)
# 
# Copyright (c) 2018 Windell H. Oskay, Evil Mad Scientist Laboratories
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gettext

import inkex
import serial


def __init__(self):
    ebbVersion = "none"


def version():
    return "0.8"  # Version number for this document


def findPort():
    # Find a single EiBotBoard connected to a USB port.
    try:
        from serial.tools.list_ports import comports
    except ImportError:
        return None
    if comports:
        com_ports_list = list(comports())
        ebb_port = None
        for port in com_ports_list:
            if port[1].startswith("EiBotBoard"):
                ebb_port = port[0]  # Success; EBB found by name match.
                break  # stop searching-- we are done.
        if ebb_port is None:
            for port in com_ports_list:
                if port[2].startswith("USB VID:PID=04D8:FD92"):
                    ebb_port = port[0]  # Success; EBB found by VID/PID match.
                    break  # stop searching-- we are done.
        return ebb_port


def listEBBports():
    # Find and return a list of all EiBotBoard units
    # connected via USB port.
    try:
        from serial.tools.list_ports import comports
    except ImportError:
        return None
    if comports:
        com_ports_list = list(comports())
        ebb_ports_list = []
        for port in com_ports_list:
            port_has_ebb = False
            if port[1].startswith("EiBotBoard"):
                port_has_ebb = True
            elif port[2].startswith("USB VID:PID=04D8:FD92"):
                port_has_ebb = True
            if port_has_ebb:
                ebb_ports_list.append(port)
        if ebb_ports_list:
            return ebb_ports_list
    return None


def testPort(com_port):
    """
    Open a given serial port, verify that it is an EiBotBoard,
    and return a SerialPort object that we can reference later.

    This routine only opens the port;
    it will need to be closed as well, for example with closePort( com_port ).
    You, who open the port, are responsible for closing it as well.

    """
    if com_port is not None:
        try:
            serial_port = serial.Serial(com_port, timeout=1.0)  # 1 second timeout!

            serial_port.flushInput()  # deprecated function name;
            # use serial_port.reset_input_buffer()
            # if we can be sure that we have pySerial 3+.

            serial_port.write('v\r'.encode('ascii'))
            str_version = serial_port.readline()
            if str_version and str_version.startswith("EBB".encode('ascii')):
                return serial_port

            serial_port.write('v\r'.encode('ascii'))
            str_version = serial_port.readline()
            if str_version and str_version.startswith("EBB".encode('ascii')):
                return serial_port
            serial_port.close()
        except serial.SerialException:
            pass
        return None
    else:
        return None


def openPort():
    # Find and open a port to a single attached EiBotBoard.
    # The first port located will be used.
    found_port = findPort()
    serial_port = testPort(found_port)
    if serial_port:
        return serial_port
    return None


def closePort(com_port):
    if com_port is not None:
        try:
            com_port.close()
        except serial.SerialException:
            pass


def query(com_port, cmd):
    if com_port is not None and cmd is not None:
        response = ''
        try:
            com_port.write(cmd.encode('ascii'))
            response = com_port.readline().decode('ascii')
            n_retry_count = 0
            while len(response) == 0 and n_retry_count < 100:
                # get new response to replace null response if necessary
                response = com_port.readline()
                n_retry_count += 1
            if cmd.strip().lower() not in ["v", "i", "a", "mr", "pi", "qm"]:
                # Most queries return an "OK" after the data requested.
                # We skip this for those few queries that do not return an extra line.
                unused_response = com_port.readline()  # read in extra blank/OK line
                n_retry_count = 0
                while len(unused_response) == 0 and n_retry_count < 100:
                    # get new response to replace null response if necessary
                    unused_response = com_port.readline()
                    n_retry_count += 1
        except:
            inkex.errormsg(gettext.gettext("Error reading serial data."))
        return response
    else:
        return None


def command(com_port, cmd):
    if com_port is not None and cmd is not None:
        try:
            com_port.write(cmd.encode('ascii'))
            response = com_port.readline().decode('ascii')
            n_retry_count = 0
            while len(response) == 0 and n_retry_count < 100:
                # get new response to replace null response if necessary
                response = com_port.readline()
                n_retry_count += 1
            if response.strip().startswith("OK"):
                pass  # inkex.errormsg( 'OK after command: ' + cmd ) #Debug option: indicate which command.
            else:
                if response:
                    inkex.errormsg('Error: Unexpected response from EBB.')
                    inkex.errormsg('   Command: {0}'.format(cmd.strip()))
                    inkex.errormsg('   Response: {0}'.format(response.strip()))
                else:
                    inkex.errormsg('EBB Serial Timeout after command: {0}'.format(cmd))
        except:
            inkex.errormsg('Failed after command: {0}'.format(cmd))
            pass


def bootload(com_port):
    # Enter bootloader mode. Do not try to read back data.
    if com_port is not None:
        try:
            com_port.write('BL\r'.encode('ascii'))
        except:
            inkex.errormsg('Failed while trying to enter bootloader.')
            pass


def queryVersion(com_port):
    return query(com_port, 'V\r')  # Query EBB Version String
