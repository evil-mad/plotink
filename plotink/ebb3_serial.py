'''
ebb3_serial.py

Serial connection utilities for EiBotBoard, firmware v3 and newer
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by the
Bantam Tools NextDraw, as well as the EggBot, WaterColorBot, AxiDraw, and
similar machines that use the EiBotBoard.

See __version__ below for version information


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

__version__ = '0.2.1'  # Dated 2024-5-28

from packaging.version import parse, InvalidVersion

from .plot_utils_import import from_dependency_import
serial = from_dependency_import('serial')
from serial.tools.list_ports import comports \
    #pylint: disable=wrong-import-position, wrong-import-order


class EBB3:
    ''' EBB3: Class for managing EiBotBoard connectivity '''

    MIN_VERSION_STRING = "3.0.2"    # Minimum supported EBB firmware version.

    def __init__(self):
        self.port_name = None       # Port name (enumeration), if any
        self.port = None            # SerialPort object, if connected. None otherwise.
        self.version = None         # EBB firmware version string (human readable), if known
        self.version_parsed = None  # Parsed EBB firmware version, if known
        self.name = None            # EBB "nickname," if known
        self.err = None             # None, or a string giving first fatal error message.
        self.caller = None          # None, or a string indicating which program opened the port


    def find_first(self):
        '''
        Find first available EiBotBoard by searching USB ports.
        Populate self.port_name, with the name of that port, if one is found.
        '''
        try:
            com_ports_list = list(comports())
        except TypeError:
            return
        ebb_port = None
        for port in com_ports_list:
            if port[1].startswith("EiBotBoard"):
                ebb_port = port[0]  # Success; EBB found by name match.
                break               # stop searching-- we are done.
        if ebb_port is None:
            for port in com_ports_list:
                if port[2].startswith("USB VID:PID=04D8:FD92"):
                    ebb_port = port[0]  # Success; EBB found by VID/PID match.
                    break               # stop searching-- we are done.
        self.port_name = ebb_port


    def reboot(self):
        ''' 
        Reboot the EBB, as though it were just powered on.
        Return True if (apparent) success, and False otherwise.
        Close port; Do not read back data.
        '''

        if (self.port is None) or (self.err is not None):
            return False
        try:
            self.port.write('RB\r'.encode('ascii'))
            self.disconnect()
            return True
        except (serial.SerialException, serial.serialutil.PortNotOpenError):
            return False


    def bootload(self):
        ''' 
        Put the EBB into bootloader mode.
        Return True if (apparent) success, and False otherwise.
        Close port; Do not read back data.
        '''
        if (self.port is None) or (self.err is not None):
            return False
        try:
            self.port.write('BL\r'.encode('ascii'))
            self.disconnect()
            return True
        except (serial.SerialException, serial.serialutil.PortNotOpenError):
            return False


    def record_error(self, message):
        ''' Record error, if it is the first error '''
        if self.err is None:
            self.err = message


    def _get_port_name(self, given_name=None):
        ''' Handle logic of locating port name with EBB '''

        if given_name is None:
            self.find_first() # Try to locate first EBB.
            if self.port_name is None:
                self.record_error("Unable to locate device on USB")
        else:
             # Try to locate named EBB
            self.port_name = find_named(given_name)
            if self.port_name is None:
                self.record_error(f"Unable to locate {given_name} on USB")


    def parse_version(self, ebb_version_string):
        '''
        Separate the version number string, and save it as a raw and parsed string.
        '''
        ebb_version_string = ebb_version_string.split("Firmware Version ", 1)

        if len(ebb_version_string) > 1:
            ebb_version_string = ebb_version_string[1]
        else:
            return # ebb_version_string is not a reasonable version number.

        ebb_version_string = ebb_version_string.strip()  # Stripped copy, for number comparisons
        self.version = ebb_version_string
        self.version_parsed = parse(ebb_version_string)


    def query_nickname(self):
        ''' Query the EBB nickname and use it to fill self.name  '''
        if (self.port is None) or (self.err is not None):
            return
        raw_string = self.query('QT')
        if raw_string is not None:
            if not raw_string.isspace():
                self.name = str(raw_string).strip()


    def write_nickname(self, nickname):
        ''' 
            Write the EBB nickname. Update self.name 
            Return True on apparent success. Return False on error.
        '''

        if (self.port is None) or (self.err is not None) or (nickname is None):
            return False

        nickname = nickname.strip()
        if not bool(nickname):
            nickname = "" # Clear nickname in this case

        try:
            self.command('ST,' + nickname)
            self.name = nickname
            return True
        except (serial.SerialException, serial.serialutil.PortNotOpenError):
            return False


    def disconnect(self):
        '''Close the serial port and set self.port to None'''
        if self.port is not None:
            try:
                self.port.close()
            except (serial.SerialException, serial.serialutil.PortNotOpenError):
                pass # We try to err on the side of trying to close the port.
        self.port = None


    def connect(self, given_name=None, caller=None):
        """
        Open a serial port, verify that it is an EiBotBoard.
        If so, save the SerialPort object in self.port and return True.

        The port to be opened will, by default, be the first one located.
        If given_name is not None, then we will only connect to the
            specific port named there. given_name may be an enumerated serial port
            or an EBB "Name tag"

        Also read the firmware version and nickname.

        Return False on failure to connect, or if the version number is too low (below 3.0.1).

        This routine only opens the port; it will need to be closed as well,
        for example with self.disconnect( ).
        You, who open the port, are responsible for closing it as well.
            An optional "caller" argument allows you to label which application
            called this function.
        """

        if self.port is not None:
            return True # Already connected and verified.

        self._get_port_name(given_name)
        if self.port_name is None:
            return False

        verified = False
        try:
            self.port = serial.Serial(self.port_name, timeout=1.0)  # 1 second timeout!
            self.port.reset_input_buffer() # Requires pyserial 3+.

            self.port.write('v\r'.encode('ascii'))    # Request version string.
            str_version = self.port.readline().decode('ascii').strip()

            if str_version:
                if "EBB" in str_version:
                    verified = True

            if not verified:
                # Second try at verifying connection, if first has failed:
                self.port.write('v\r'.encode('ascii'))    # Request version string.
                str_version = self.port.readline().decode('ascii').strip()
                if str_version:
                    if "EBB" in str_version:
                        verified = True

        except serial.SerialException:
            self.record_error(f"Error testing USB connection (port name: {self.port_name})")
            self.disconnect() # Try to close the port, in case it is open.

        if not verified:
            self.record_error(f"Failed to connect via USB (port name: {self.port_name})")
            self.disconnect() # Try to close the port, in case it is open.
            return False

        self.parse_version(str_version) # Parse firmware version

        if not self.min_version(self.MIN_VERSION_STRING):
            error_msg = f"Firmware version ({self.version}) not supported.\n"
            error_msg += f"Firmware {self.MIN_VERSION_STRING} or newer is required.\n"
            error_msg += "Visit https://bantam.tools/ndfw to update your firmware."
            self.record_error(error_msg)
            return False

        # Special command to enter "future" syntax mode, before using self.command for everything.
        self.port.write( "CU,10,1\r".encode('ascii')) # Set future syntax mode
        self.port.readline()   # Ignore response, which may be in legacy or future syntax
        self.port.reset_input_buffer()                # clear input buffer

        self.query_nickname()
        if caller is not None:
            self.caller = caller
        return True


    def min_version(self, version_string):
        '''
        Return True if the EBB firmware version is at least version_string.
        Return False if the EBB firmware version is below version_string.
        Return None if version_string cannot be parsed as a version number. 
        '''

        try:
            parsed_version_string = parse(version_string)
        except InvalidVersion:
            return None
        if self.version_parsed >= parsed_version_string:
            return True
        return False


    def command(self, cmd):
        '''
        Send a command to the EBB.
        Returns True if command apparently successful.
        Returns False if an error is encountered;
            First error encountered will be written to self.err.
        '''

        if (self.port is None) or (self.err is not None) or (cmd is None):
            return False

        cmd = cmd.strip() # Remove leading, trailing whitespace, if any.

        if len(cmd) == 1:
            cmd_name = cmd[0]       # Case of single-letter command.
        elif cmd[1] == ',':
            cmd_name = cmd[0]       # Case of single-letter command with arguments.
        else:
            cmd_name = cmd[0:2]     # All other cases: Command names are two letters long.

        response = ''
        try:
            self.port.write((cmd + '\r').encode('ascii'))
            response = self.port.readline().decode('ascii').strip()

            n_retry_count = 0
            while len(response) == 0 and n_retry_count < 25:
                # get new response to replace null response if necessary
                response = self.port.readline().decode('ascii').strip()
                n_retry_count += 1

            if not response.startswith(cmd_name):
                if response:
                    error_msg = '\nUnexpected response from EBB.' +\
                       f'    Command: {cmd}\n    Response: {response}'
                else:
                    error_msg = f'EBB Serial Timeout after command: {cmd}'
                self.record_error(error_msg)

        except (serial.SerialException, IOError, RuntimeError, OSError):
            if cmd_name.lower() not in ["rb", "r", "bl"]: # Ignore err on these commands
                error_msg = f'USB communication error after command: {cmd}'
                self.record_error(error_msg)
        if 'Err:' in response:
            error_msg = 'Error reported by EBB.\n' +\
               f'    Command: {cmd}\n    Response: {response}'
            self.record_error(error_msg)

        return bool(self.err is None) # Return True if no error, False if error.


    def query(self, qry):
        '''
        General function to send a query to the EiBotBoard. Like command, but returns a reponse.
        Works using the EBB 3 "future" syntax only. Responses are returned with the query prefix
            and whitespace removed, so if the `QG` command would return `QG,3E<NL>`, this
            function returns only `3E`.
        Returns None if an error is encountered.
            First error encountered will be written to self.err.
        This function does not support the following query codes: 
            "CK" (development test function), "A" (deprecated).
        '''

        if (self.port is None) or (self.err is not None) or (qry is None):
            return None

        qry = qry.strip() # Remove leading, trailing whitespace, if any.

        if len(qry) == 1:
            qry_name = qry[0]       # Case of single-letter command/query
        elif qry[1] == ',':
            qry_name = qry[0]       # Case of single-letter command with arguments.
        else:
            qry_name = qry[0:2]     # Cases except QU: Query responses are two letters long.

        response = ''
        try:
            self.port.write((qry + '\r').encode('ascii'))
            response = self.port.readline().decode('ascii').strip()

            n_retry_count = 0
            while len(response) == 0 and n_retry_count < 25:
                # get new response to replace null response if necessary
                response = self.port.readline().decode('ascii').strip()
                n_retry_count += 1

        except (serial.SerialException, IOError, RuntimeError, OSError):
            if qry_name.lower() not in ["rb", "r", "bl"]: # Ignore err on these commands
                error_msg = f'USB communication error after query: {qry}'
                self.record_error(error_msg)
                return None

        if ('Err:' in response) or (not response.startswith(qry_name)):
            if response:
                error_msg = '\nUnexpected response from EBB.' +\
                   f'    Query: {qry}\n    Response: {response}'
            else:
                error_msg = f'EBB Serial Timeout after query: {qry}'
            self.record_error(error_msg)
            return None

        header_len = len(qry_name)
        if len(response) > header_len:      # Response is longer than the query length.
            if response[header_len] == ',': # Check if character after query is a comma.
                header_len += 1             # If so, strip it out of response too.

        return response[header_len:] # Strip off leading repetition of command name.


    def query_statusbyte(self):
        '''
        Special function to manage the `QG` query and return an integer
        representing the contents of the status byte.
        '''

        if (self.port is None) or (self.err is not None):
            return None

        response = ''
        try:
            self.port.write('QG\r'.encode('ascii'))
            response = self.port.readline().decode('ascii').strip()

            if not response.startswith('QG'):
                if response:
                    error_msg = '\nUnexpected response from EBB.' +\
                       f'    Response to QG query: {response}'
                else:
                    error_msg = 'EBB Serial Timeout while reading status byte.'
                self.record_error(error_msg)

        except (serial.SerialException, IOError, RuntimeError, OSError):
            error_msg = 'USB communication error after status byte query'
            self.record_error(error_msg)
            return None

        if 'Err:' in response:
            error_msg = 'Error reported by EBB.\n' +\
               f'    Query: QG\n    Response: {response}'
            self.record_error(error_msg)
            return None
        try:
            return int(response[3:], 16) # Strip off query name ("QG,") and convert to int.
        except (TypeError, ValueError):
            return None

    def var_write(self, value, index):
        """
        Store a variable in (volatile) EBB RAM using SL command.

        value is an integer between 0 and 255.
        index is an integer between 0 and 31.

        Values can be read with var_read().
        Return True on apparent success, False on apparent failure.
        """
        if (self.port is None) or (self.err is not None):
            return False

        self.command(f'SL,{value},{index}')

        if self.err is not None:
            return False
        return True


    def var_read(self, index):
        """
        Read a variable from (volatile) EBB RAM using QL command.
        index is an integer between 0 and 31.

        Values can be written with var_write().

        Return value read on apparent success, None on apparent failure.
        """
        if (self.port is None) or (self.err is not None):
            return None

        value = self.query(f'QL,{index}')

        if self.err is not None:
            return None
        return int(value)


    def var_write_int32(self, value, start_index):
        """
        Store a 4-byte variable in (volatile) EBB RAM, using four slots
            of the RAM as addressed by var_write (SL command).

        value is a signed 32-bit integer, -2147483648 to 2147483647.
        start_index is an integer between 0 and 28.

        The number will be stored as four 8-bit unsigned ints, at indices
            start_index, start_index+1, start_index+2, start_index+3.

        Values can be read with var_read_int32().
        Return True on apparent success, False on apparent failure.
        """
        if (self.port is None) or (self.err is not None):
            return False

        bytes_sequence = value.to_bytes(4, byteorder='big', signed=True)

        for byte in bytes_sequence:
            self.var_write(byte, start_index)
            start_index += 1

        if self.err is not None:
            return False
        return True


    def var_read_int32(self, start_index):
        """
        Read a 4-byte variable from (volatile) EBB RAM, using four slots
            of the RAM as addressed by var_write (SL command).

        start_index is an integer between 0 and 28.

        The number will be read from four 8-bit unsigned ints, at indices
            start_index, start_index+1, start_index+2, start_index+3.

        Values can be written with var_write_int32().
        Return a signed integer, on apparent success; Return None on error.
        """
        if (self.port is None) or (self.err is not None):
            return False

        bytes_sequence = []

        for byte_offset in range(0,4):
            value = self.var_read(start_index + byte_offset)
            byte_offset += 1
            bytes_sequence.append(value)

        if self.err is not None:
            return None
        return int.from_bytes(bytes_sequence, byteorder='big', signed=True)


def list_ebb_ports():
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
    ebb_ports_list = list_ebb_ports()
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
            ebb_names_list.append(p_0)
    return ebb_names_list


def find_named(port_name=None):
    '''
    Find a specific EiBotBoard identified by a string giving either:
           The enumerated serial port, or
           An EBB "Name tag"
    Names should be 3-16 characters long. Comparisons are not case sensitive.
    (Name tags may assigned with the ST command.)
    If found:     return port_name (enumeration
    '''

    if port_name is None:
        return None

    needle = 'SER=' + port_name     # pyserial 3
    needle2 = '(' + port_name + ')' # e.g., "(COM4)"

    needle = needle.lower()
    needle2 = needle2.lower()
    plower = port_name.lower()

    try:
        com_ports_list = list(comports())
    except TypeError:
        return None

    for port in com_ports_list:
        p_0 = port[0].lower()
        p_1 = port[1].lower()
        p_2 = port[2].lower()

        if (needle in p_2) or (needle2 in p_1):
            return port[0]  # Success; EBB found by name match.

        p_1 = p_1[11:]
        if (p_1.startswith(plower)) or (p_0.startswith(plower)):
            return port[0]  # Success; EBB found by name match.

        needle.replace(" ", "_") # SN on Windows has underscores, not spaces.
        if needle in p_2:
            return port[0]  # Success; EBB found by port match.
    return None
