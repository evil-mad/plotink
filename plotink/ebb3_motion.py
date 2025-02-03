'''
ebb3_motion.py

Motion control and command utilities for EiBotBoard, firmware v3 and newer
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by the
Bantam Tools NextDraw, as well as the EggBot, WaterColorBot, AxiDraw, and
similar machines that use the EiBotBoard.

See __version__ below for version information


The MIT License (MIT)

Copyright (c) 2025 Windell H. Oskay, Bantam Tools

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

__version__ = '0.2'  # Dated 2025-02-02

from . import ebb3_serial

class EBBMotionWrap(ebb3_serial.EBB3):
    ''' EBBMotionWrap: Wrapper class for managing low-level EiBotBoard
        motion and data management commands and queries
    '''
    #pylint: disable=too-many-public-methods

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

        if (position1 is not None) and (position2 is not None):
            str_output = f'HM,{rate},{position1},{position2}'
        else:
            str_output = f'HM,{rate}'
        self.command(str_output)


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


    def clear_steps(self):
        """
        Set the two step counters and motion accumulators to zero.
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command('CS')


    def clear_accumulators(self):
        """
        Set the two motion accumulators to zero.
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command('T3,1,0,0,0,0,0,0,3')


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


    def dio_b_config(self, pin, state, direction):
        """
        Enable an I/O pin on port b. 
            Pin: 0-7, but typically one of 0-3. 
            State: 0 or 1.
            Direction: 0: output, 1: input
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command(f'PO,B,{pin},{state}')     # Set initial Bx pin value, high or low:
        self.command(f'PD,B,{pin},{direction}') # Configure I/O pin as output or input


    def dio_b_set(self, pin, state):
        """
        Set the value of an I/O pin on port b. 
            Configure the pin with dio_b_config() before calling this.
            Pin: 0-7, but typically one of 0-3. 
            State: 0 or 1.
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command(f'PO,B,{pin},{state}')     # Set Bx pin value, high or low:


    def dio_b_read(self, pin):
        """
        Read the value of an I/O pin on port b. 
            Configure the pin with dio_b_config() before calling this.
            Pin: 0-7, but typically one of 0-3. 
            State: 0 or 1.
        Return True or False, depending on pin value, or None in case of error.
        """
        if (self.port is None) or (self.err is not None):
            return None
        response = self.query(f'PI,B,{pin}')
        if response is None:
            return None
        return bool(int(response))


    def pen_pos_down(self, servo_max):
        """ Set pen down position using SC http://evil-mad.github.io/EggBot/ebb.html#SC
            servo_max may be in the range 1 to 65535, in units of 83 ns intervals.
            This sets the "Pen Down" position.
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command(f"SC,5,{servo_max}")


    def pen_pos_up(self, servo_min):
        """ Set pen up position using SC http://evil-mad.github.io/EggBot/ebb.html#SC
            servo_max may be in the range 1 to 65535, in units of 83 ns intervals.
            This sets the "Pen Up" position.
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command(f"SC,4,{servo_min}")


    def pen_rate_down(self, pen_down_rate):
        """ Set pen lowering speed using SC
            rate may be in the range 1 to 65535
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command(f"SC,12,{pen_down_rate}")


    def pen_rate_up(self, pen_up_rate):
        """ Set pen raising speed using SC
            rate may be in the range 1 to 65535
        """
        if (self.port is None) or (self.err is not None):
            return
        self.command(f"SC,11,{pen_up_rate}")


    def servo_timeout(self, timeout_ms, state=None):
        """
        Set the EBB servo motor timeout, for old-style (brushed)
            pen-lift servo motors.
        The EBB will cut power to the pen-lift servo motor after a given
        time delay since the last X/Y/Z motion command.
        It can also optionally set an immediate on/off state.

        The time delay timeout_ms is given in ms. A value of 0 will
        disable the automatic power-off feature.

        The state parameter is given as 0 or 1, to turn off or on
        servo power immediately, respectively.

        This feature requires EBB hardware v 2.5.0 or newer

        Reference: http://evil-mad.github.io/EggBot/ebb.html#SR
        """
        if (self.port is None) or (self.err is not None):
            return
        if state is None:
            str_output = f'SR,{timeout_ms}'
        else:
            str_output = f'SR,{timeout_ms},{state}'
        self.command(str_output)


    def query_voltage(self, threshold=None):
        """
        Query the EBB motor power supply input voltage.
        Return True if power seems to be on, False if not. None on error.
        This function is for a spot check on voltage, not continuous
            monitoring.
        (The separate query_current() function can return an integer value.)
        """
        if (self.port is None) or (self.err is not None):
            return None
        if threshold is None:
            threshold = 250 # Typical threshold, when using 9 V power supply.
        split_string = self.query('QC').split(",", 1)
        split_len = len(split_string)
        if split_len > 1:
            voltage_value = int(split_string[1])  # Pick second value only
        else:
            return None  # We haven't received a reasonable voltage string response.
        if voltage_value < threshold:
            return False
        return True


    def query_current(self):
        """
        Query the EBB motor current setpoint and voltage readouts,
            return values as integers.
        """
        if (self.port is None) or (self.err is not None):
            return None, None
        split_string = self.query('QC').split(",", 1)
        split_len = len(split_string)
        if split_len > 1:
            return int(split_string[0]), int(split_string[1])
        return None, None
