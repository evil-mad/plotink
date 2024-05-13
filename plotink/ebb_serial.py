'''
ebb_serial.py

Serial connection utilities for EiBotBoard
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by the
Bantam Tools NextDraw, as well as the EggBot, WaterColorBot, AxiDraw, and
similar machines that use the EiBotBoard.

See __version__ below for version information

Thanks to Shel Michaels for bug fixes and helpful suggestions.


The MIT License (MIT)

Copyright (c) 2024 Windell H. Oskay, Bantam Tools

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__version__ = '0.3'  # Dated 2024-5-13

import logging
from packaging.version import parse

from .plot_utils_import import from_dependency_import
inkex = from_dependency_import('ink_extensions.inkex')
serial = from_dependency_import('serial')
from serial.tools.list_ports import comports \
    #pylint: disable=wrong-import-position, wrong-import-order

logger = logging.getLogger(__name__)

def version():
    '''Version number for this document'''
    return __version__


def findPort():
    '''
    Find first available EiBotBoard by searching USB ports. Return serial port name.
    '''
    try:
        com_ports_list = list(comports())
    except TypeError:
        return None
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


def find_named_ebb(port_name):
    '''
    Find a specific EiBotBoard identified by a string giving either:
           The enumerated serial port, or
           An EBB "Name tag"
    Names should be 3-16 characters long. Comparisons are not case sensitive.
    (Name tags may assigned with the ST command on firmware 2.5.5 and later.)
    If found:     Return serial port name (enumeration)
    If not found, Return None
    '''
    if port_name is not None:
        needle = 'SER=' + port_name     # pyserial 3
        needle2 = 'SNR=' + port_name    # pyserial 2.7
        needle3 = '(' + port_name + ')' # e.g., "(COM4)"

        needle = needle.lower()
        needle2 = needle2.lower()
        needle3 = needle3.lower()
        plower = port_name.lower()

        try:
            com_ports_list = list(comports())
        except TypeError:
            return None

        for port in com_ports_list:
            p_0 = port[0].lower()
            p_1 = port[1].lower()
            p_2 = port[2].lower()

            if needle in p_2:
                return port[0]  # Success; EBB found by name match.
            if needle2 in p_2:
                return port[0]  # Success; EBB found by name match.
            if needle3 in p_1:
                return port[0]  # Success; EBB found by port match.

            p_1 = p_1[11:]
            if p_1.startswith(plower):
                return port[0]  # Success; EBB found by name match.
            if p_0.startswith(plower):
                return port[0]  # Success; EBB found by port match.

            needle.replace(" ", "_") # SN on Windows has underscores, not spaces.
            if needle in p_2:
                return port[0]  # Success; EBB found by port match.

            needle2.replace(" ", "_") # SN on Windows has underscores, not spaces.
            if needle2 in p_2:
                return port[0]  # Success; EBB found by port match.
    return None


def query_nickname(port_name, verbose=True):
    '''
    Query the EBB nickname and report it.
    If verbose is True or omitted, the result will be human readable.
    A short version is returned if verbose is False.
    Requires firmware version 2.5.5 or newer. http://evil-mad.github.io/EggBot/ebb.html#QT
    '''
    if port_name is not None:
        version_status = min_version(port_name, "2.5.5")

        if version_status:
            raw_string = (query(port_name, 'QT\r'))
            if raw_string.isspace():
                if verbose:
                    return "This AxiDraw does not have a nickname assigned."
                return None
            if verbose:
                return "AxiDraw nickname: " + raw_string
            return str(raw_string).strip()
        if version_status is False:
            if verbose:
                return "AxiDraw naming requires firmware version 2.5.5 or higher."
    return None


def write_nickname(port_name, nickname):
    '''
    Write the EBB nickname.
    Requires firmware version 2.5.5 or newer. http://evil-mad.github.io/EggBot/ebb.html#ST
    '''
    if port_name is not None:
        version_status = min_version(port_name, "2.5.5")

        if version_status:
            try:
                cmd = 'ST,' + nickname + '\r'
                command(port_name,cmd)
                return True
            except:
                return False
    return None


def reboot(port_name):
    '''
    Reboot the EBB, as though it were just powered on.
    Requires firmware version 2.5.5 or newer. http://evil-mad.github.io/EggBot/ebb.html#RB
    '''
    if port_name is not None:
        version_status = min_version(port_name, "2.5.5")
        if version_status:
            try:
                command(port_name,'RB\r')
            except:
                pass


def list_port_info():
    '''Find and return a list of all USB devices and their information.'''
    try:
        com_ports_list = list(comports())
    except TypeError:
        return None

    port_info_list = []
    for port in com_ports_list:
        port_info_list.append(port[0]) # port name
        port_info_list.append(port[1]) # Identifier
        port_info_list.append(port[2]) # VID/PID
    if port_info_list:
        return port_info_list
    return None


def listEBBports():
    '''Find and return a list of all EiBotBoard units connected via USB port.'''

    try:
        com_ports_list = list(comports())
    except TypeError:
        return None
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


def list_named_ebbs():
    '''Return descriptive list of all EiBotBoard units'''
    ebb_ports_list = listEBBports()
    if not ebb_ports_list:
        return None
    ebb_names_list = []
    for port in ebb_ports_list:
        name_found = False
        p_0 = port[0]
        p_1 = port[1]
        p_2 = port[2]
        if p_1.startswith("EiBotBoard"):
            temp_string = p_1[11:]
            if temp_string:
                if temp_string is not None:
                    ebb_names_list.append(temp_string)
                    name_found = True
        if not name_found:
            # Look for "SER=XXXX LOCAT" pattern,
            #  typical of Pyserial 3 on Windows.
            if 'SER=' in p_2 and ' LOCAT' in p_2:
                index1 = p_2.find('SER=') + len('SER=')
                index2 = p_2.find(' LOCAT', index1)
                temp_string = p_2[index1:index2]
                if len(temp_string) < 3:
                    temp_string = None
                if temp_string is not None:
                    ebb_names_list.append(temp_string)
                    name_found = True
        if not name_found:
            # Look for "...SNR=XXXX" pattern,
            #  typical of Pyserial 2.7 on Windows
            if 'SNR=' in p_2:
                index1 = p_2.find('SNR=') + len('SNR=')
                index2 = len(p_2)
                temp_string = p_2[index1:index2]
                if len(temp_string) < 3:
                    temp_string = None
                if temp_string is not None:
                    ebb_names_list.append(temp_string)
                    name_found = True
        if not name_found:
            ebb_names_list.append(p_0)
    return ebb_names_list


def testPort(port_name):
    """
    Open a specific serial port with name port_name, verify that it is an EiBotBoard,
    and return a SerialPort object that we can reference later.

    This routine only opens the port; it will need to be closed as well,
    for example with closePort( port_name ).
    You, who open the port, are responsible for closing it as well.
    """
    if port_name is not None:
        try:
            serial_port = serial.Serial(port_name, timeout=1.0)  # 1 second timeout!

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
        except serial.SerialException as err:
            logger.error("Error testing serial port `{}` connection".format(port_name))
            logger.info("Error context:", exc_info=err)
    return None


def openPort():
    '''
    Find and open a port to a single attached EiBotBoard.
    The first port located will be used.
    '''
    found_port = findPort()
    serial_port = testPort(found_port)
    if serial_port:
        return serial_port
    return None


def open_named_port(port_name):
    '''
    Find and open a port to a single attached EiBotBoard, indicated by name.
    The first port located will be used.
    '''
    found_port = find_named_ebb(port_name)
    serial_port = testPort(found_port)
    if serial_port:
        return serial_port
    return None


def closePort(port_name):
    '''Close the given serial port.'''
    if port_name is not None:
        try:
            port_name.close()
        except serial.SerialException:
            pass


def query(port_name, cmd, verbose=True):
    '''General command to send a query to the EiBotBoard'''
    if port_name is not None and cmd is not None:
        response = ''
        try:
            port_name.write(cmd.encode('ascii'))
            response = port_name.readline().decode('ascii')
            n_retry_count = 0
            while len(response) == 0 and n_retry_count < 100:
                # get new response to replace null response if necessary
                response = port_name.readline()
                n_retry_count += 1
            if cmd.split(",")[0].strip().lower() not in ["a", "i", "mr", "pi", "qm", "qg", "v"]:
                # Most queries return an "OK" after the data requested.
                # We skip this for those few queries that do not return an extra line.
                unused_response = port_name.readline()  # read in extra blank/OK line
                n_retry_count = 0
                while len(unused_response) == 0 and n_retry_count < 100:
                    # get new response to replace null response if necessary
                    unused_response = port_name.readline()
                    n_retry_count += 1
        except (serial.SerialException, IOError, RuntimeError, OSError) as err:
            if verbose:
                logger.error("Error reading serial data")
            else:
                logger.info("Error reading serial data")
            logger.info("Error context:", exc_info=err)

        if 'Err:' in response:
            error_msg = '\n'.join(('Unexpected response from EBB.',
               '    Command: {0}'.format(cmd.strip()),
               '    Response: {0}'.format(response.strip())))
            if verbose:
                logger.error(error_msg)
            else:
                logger.info(error_msg)
        return response
    return None


def command(port_name, cmd, verbose=True):
    '''General command to send a command to the EiBotBoard'''
    if port_name is not None and cmd is not None:
        try:
            port_name.write(cmd.encode('ascii'))
            response = port_name.readline().decode('ascii')
            n_retry_count = 0
            while len(response) == 0 and n_retry_count < 100:
                # get new response to replace null response if necessary
                response = port_name.readline().decode('ascii')
                n_retry_count += 1
            if response.strip().startswith("OK"):
                # Debug option: indicate which command:
                # inkex.errormsg( 'OK after command: ' + cmd )
                pass
            else:
                if response:
                    error_msg = '\n'.join(('Unexpected response from EBB.',
                                           '    Command: {0}'.format(cmd.strip()),
                                           '    Response: {0}'.format(response.strip())))
                else:
                    error_msg = 'EBB Serial Timeout after command: {0}'.format(cmd)
                if verbose:
                    logger.error(error_msg)
                else:
                    logger.info(error_msg)
        except (serial.SerialException, IOError, RuntimeError, OSError) as err:
            if cmd.strip().lower() not in ["rb"]: # Ignore error on reboot (RB) command
                if verbose:
                    logger.error('Failed after command: {0}'.format(cmd))
                else:
                    logger.info('Failed after command: {0}'.format(cmd))
                logger.info("Error context:", exc_info=err)


def bootload(port_name):
    '''Enter bootloader mode. Do not try to read back data.'''
    if port_name is not None:
        try:
            port_name.write('BL\r'.encode('ascii'))
            return True
        except:
            return False
    return None


def min_version(port_name, version_string):
    '''
    Query the EBB firmware version for the EBB located at port_name.
    Return True if the EBB firmware version is at least version_string.
    Return False if the EBB firmware version is below version_string.
    Return None if we are unable to determine True or False.
    '''
    if port_name is not None:
        ebb_version_string = queryVersion(port_name)  # Full string, human readable
        ebb_version_string = ebb_version_string.split("Firmware Version ", 1)

        if len(ebb_version_string) > 1:
            ebb_version_string = ebb_version_string[1]
        else:
            return None  # We haven't received a reasonable version number response.

        ebb_version_string = ebb_version_string.strip()  # Stripped copy, for number comparisons
        if parse(ebb_version_string) >= parse(version_string):
            return True
        return False
    return None


def queryVersion(port_name):
    '''Query EBB Version String'''
    return query(port_name, 'V\r', True)
