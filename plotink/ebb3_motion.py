'''
ebb3_motion.py

Motion control and command utilities for EiBotBoard, firmware v3 and newer
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by
Bantam Tools NextDraw, EggBot, WaterColorBot, AxiDraw, and similar machines.

See __version__ below for version number.

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

__version__ = '0.1'  # Dated 2024-3-18

from . import ebb3_serial
from . import ebb_calc

class EBBMotionWrap(ebb3_serial.EBB3):
    ''' EBBMotionWrap: Wrapper class for managing EiBotBoard basic motion commands '''

    def __init__(self):
        ebb3_serial.EBB3.__init__(self)

    def timed_pause(self, pause_time):
        ''' "Hardware" pause on EBB control board, for pause_time milliseconds '''
        if (self.port is None) or (self.err is not None):
            return

        while pause_time > 0:
            if pause_time > 750:
                time_delay = 750
            else:
                time_delay = max(pause_time, 1) # don't allow zero-time moves
            self.command(f'SM,{time_delay},0,0')
            pause_time -= time_delay

    def xy_move(self, delta_x, delta_y, duration):
        '''
        Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
        On machines where the two motor move independent axes, this is typically
        wired upsuch that axis 1 is the Y axis and axis 2 is the X axis of motion.
        On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
        Machines like AxiDraw and the Bantam Tools NextDraw use mixed axes.
        '''
        if (self.port is None) or (self.err is not None):
            return

        str_output = f'SM,{duration},{delta_y},{delta_x}'
        self.command(str_output)

    def abs_move(self, rate, position1=None, position2=None):
        '''
        Absolute XY or move to (0,0) step position as: "HM,<rate>[,<position1>,<position2>]<CR>"
            See http://evil-mad.github.io/EggBot/ebb.html#HM for more information

        This is an "absolute" move, to a position relative to where the motors
        were enabled. It is not necessarily a move in a straight line.
        If both position1 and position2 are given, then move to the given position.
        Otherwise, return to the position where the motors were enabled/zeroed.
        '''
        if (self.port is None) or (self.err is not None):
            return

        if position1 and position2:
            str_output = f'HM,{rate},{position1},{position2}'
        else:
            str_output = f'HM,{rate}'
        self.command(str_output)

    # Note: QueryPenUp() is not present in this module; use QG instead.
    # Note: QueryPRGButton() is not present in this module; use QG instead.

    def motors_disable(self):
        """ Disable stepper motors with EM command """

        if (self.port is None) or (self.err is not None):
            return
        self.command('EM,0,0')


    def motors_enable(self, resolution_1, resolution_2):
        """
        Enable one or both motors with EM command at selected resolution.
            If resolution == 0, -> Motor disabled
            If resolution == 1, -> 16X microstepping
            If resolution == 2, -> 8X microstepping
            If resolution == 3, -> 4X microstepping
            If resolution == 4, -> 2X microstepping
            If resolution == 5, -> No microstepping
        There is some subtlety to how the EM command operates. Only resolution_1 actually
            sets the resolution scale; "resolution_2" only controls motor 2 on or off.
            See docs for details: https://evil-mad.github.io/EggBot/ebb.html#EM
        """

        if (self.port is None) or (self.err is not None):
            return

        resolution_1 = max(int(resolution_1), 0)
        resolution_1 = min(resolution_1, 5)
        resolution_2 = max(int(resolution_2), 0)
        resolution_2 = min(resolution_2, 5)

        # If we are enabling only one motor, use the 'CU,50" configuration option to
        #   permit only one motor to be enabled.
        if (resolution_1 != resolution_2) and (resolution_1 * resolution_2 == 0):
            self.command('CU,50,0')

        # If we are enabling _only_ motor 2, then we actually need to set the resolution
        #   scale, by enabling motor 1 at that resolution -- IF that is not the resolution
        #   scale already in use -- before enabling the motors in the normal way.

        if (resolution_1 == 0) and (resolution_2 != 0):
            old_res = 0
            motor_res = self.motors_query_enabled()
            if motor_res is None:       # Indicates error while reading motor states.
                return
            if motor_res[1] != 0:
                old_res = motor_res[1]
            if motor_res[0] != 0:
                old_res = motor_res[0]

            if old_res != resolution_2:
                # print(f'Sending: EM,{resolution_2},{resolution_2}')
                self.command(f'EM,{resolution_2},{resolution_2}')

        self.command(f'EM,{resolution_1},{resolution_2}')
        # print(f'Sending: EM,{resolution_1},{resolution_2}')


    def motors_query_enabled(self):
        """
        Read current state of motors and their resolution with QE command.
        Returns: res_1, res_2, which are integers corresponding to the command values
            that are used when _enabling motors_, defined by this table:

            0: Motor disabled
            1: Motor enabled; global step mode is 1/16 step mode
            2: Motor enabled; global step mode is 1/8 step mode
            3: Motor enabled; global step mode is 1/4 step mode
            4: Motor enabled; global step mode is 1/2 step mode
            5: Motor enabled; global step mode is full step mode

            To get there, we decode the values that the QE command returns, which are
            0: Motor disabled,                  1: Enabled w/o microstepping.
            2: Enabled with 2X microstepping,   4: Enabled with 4X microstepping
            8: Enabled with 8X microstepping,  16: Enabled with 16X microstepping.

        In case of error, return None.
        """
        if (self.port is None) or (self.err is not None):
            return None

        response = self.query("QE")
        if response is None:
            return None

        res_map = {16: 1, 8: 2, 4: 3, 2: 4, 1: 5, 0:0} # Decode QE query values to EM command values

        res_list = response.split(',')
        return res_map[int(res_list[0])], res_map[int(res_list[1])]


    def query_steps(self):
        """
        Read current step positions using QS command.
        Returns: steps_1, steps_2 as integers, or None in case of error.
        """

        if (self.port is None) or (self.err is not None):
            return None

        result = self.query('QS') # Query global step position
        if self.err:
            return None

        result_list = result.strip().split(",")
        return int(result_list[0]), int(result_list[1])

    def pen_lower(self, pen_delay, pin=None):
        """
        Lower pen with SP command
        Optionally, specify which pin to use
        """
        if (self.port is None) or (self.err is not None):
            return
        if pin:
            str_output = f'SP,0,{pen_delay},{pin}'
        else:
            str_output = f'SP,0,{pen_delay}'
        self.command(str_output)

    def pen_raise(self, pen_delay, pin=None):
        """
        Raise pen with SP command
        Optionally, specify which pin to use
        """
        if (self.port is None) or (self.err is not None):
            return
        if pin:
            str_output = f'SP,1,{pen_delay},{pin}'
        else:
            str_output = f'SP,1,{pen_delay}'
        self.command(str_output)






###################



def PBOutConfig(port_name, pin, state, verbose=True):
    """
    Enable an I/O pin. Pin: {0, 1, 2, or 3}. State: {0 or 1}.
    Note that B0 is used as an alternate pause button input.
    Note that B1 is used as the pen-lift servo motor output.
    Note that B3 is used as the EggBot engraver output.
    For use with a laser (or similar implement), pin 3 is recommended
    """
    if port_name is not None:
        # Set initial Bx pin value, high or low:
        str_output = 'PO,B,{0},{1}\r'.format(pin, state)
        ebb_serial.command(port_name, str_output, verbose)
        # Configure I/O pin Bx as an output
        str_output = 'PD,B,{0},0\r'.format(pin)
        ebb_serial.command(port_name, str_output, verbose)


def PBOutValue(port_name, pin, state, verbose=True):
    """
    Set state of the I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
    Set the pin as an output with OutputPinBConfigure before using this.
    """
    if port_name is not None:
        str_output = 'PO,B,{0},{1}\r'.format(pin, state)
        ebb_serial.command(port_name, str_output, verbose)


def TogglePen(port_name, verbose=True):
    """ Toggle pen state using TP """
    if port_name is not None:
        ebb_serial.command(port_name, 'TP\r', verbose)


def setPenDownPos(port_name, servo_max, verbose=True):
    """ Set pen down position using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,5,{0}\r'.format(servo_max), verbose)
        # servo_max may be in the range 1 to 65535, in units of 83 ns intervals.
        # This sets the "Pen Down"position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenDownRate(port_name, pen_down_rate, verbose=True):
    """ Set pen lowering speed using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,12,{0}\r'.format(pen_down_rate), verbose)
        # Set the rate of change of the servo when going down.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpPos(port_name, servo_min, verbose=True):
    """ Set pen up position using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,4,{0}\r'.format(servo_min), verbose)
        # servo_min may be in the range 1 to 65535, in units of 83 ns intervals.
        # This sets the "Pen Up" position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpRate(port_name, pen_up_rate, verbose=True):
    """ Set pen raising speed using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,11,{0}\r'.format(pen_up_rate), verbose)
        # Set the rate of change of the servo when going up.
        # http://evil-mad.github.io/EggBot/ebb.html#SC





def queryVoltage(port_name, verbose=True):
    """ Query the EBB motor power supply input voltage. """
    if port_name is not None:
        if not ebb_serial.min_version(port_name, "2.2.3"):
            return True # Unable to read version, or version is below 2.2.3.
                        # In these cases, issue no voltage warning.
        raw_string = ebb_serial.query(port_name, 'QC\r', verbose)
        split_string = raw_string.split(",", 1)
        split_len = len(split_string)
        if split_len > 1:
            voltage_value = int(split_string[1])  # Pick second value only
        else:
            return True  # We haven't received a reasonable voltage string response.
            # Ignore voltage test and return.
        # Typical reading is about 300, for 9 V input.
        if voltage_value < 250:
            return False
    return True
