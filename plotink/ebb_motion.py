# ebb_motion.py
'''

Motion control utilities for EiBotBoard
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

__version__ = '0.27'  # Dated 2024-05-13


from . import ebb_serial
from . import ebb_calc

def version():  # Report version number for this document
    ''' Return version number '''
    return __version__

def doABMove(port_name, delta_a, delta_b, duration, verbose=True):
    '''
    Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>"
    Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
    '''
    if port_name is not None:
        str_output = 'XM,{0},{1},{2}\r'.format(duration, delta_a, delta_b)
        ebb_serial.command(port_name, str_output, verbose)


def doTimedPause(port_name, n_pause, verbose=True):
    ''' "Hardware" pause on EBB control board '''
    if port_name is not None:
        while n_pause > 0:
            if n_pause > 750:
                time_delay = 750
            else:
                time_delay = n_pause
                if time_delay < 1:
                    time_delay = 1  # don't allow zero-time moves
            ebb_serial.command(port_name, 'SM,{0},0,0\r'.format(time_delay), verbose)
            n_pause -= time_delay


def doLowLevelMove(port_name, rate1, steps1, accel1, rate2, steps2,
    accel2, clear=None, verbose=True):
    '''
    Execute a "pre-computed" 2D movement of the form
      "LM,<Rate1>,<Steps1>,<Accel1>,<Rate2>,<Steps2>,<Accel2>[,Clear]<CR>"
      See http://evil-mad.github.io/EggBot/ebb.html#LM for documentation.
    Requires firmware version 2.7.0 or higher for proper operation
    '''
    if port_name is not None:
        if ((rate1 == 0 and accel1 == 0) or steps1 == 0) and\
                ((rate2 == 0 and accel2 == 0) or steps2 == 0):
            return # No steps to take on either axis
        if clear:
            str_output = 'LM,{0},{1},{2},{3},{4},{5},{6}\r'.format(rate1,\
                                    steps1, accel1, rate2, steps2, accel2, clear)
        else:
            str_output = 'LM,{0},{1},{2},{3},{4},{5}\r'.format(rate1,\
                                steps1, accel1, rate2, steps2, accel2)
        ebb_serial.command(port_name, str_output, verbose)


def doXYMove(port_name, delta_x, delta_y, duration, verbose=True):
    '''
    Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
    Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
    On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
    '''
    if port_name is not None:
        str_output = 'SM,{0},{1},{2}\r'.format(duration, delta_y, delta_x)
        ebb_serial.command(port_name, str_output, verbose)


def doAbsMove(port_name, rate, position1=None, position2=None, verbose=True):
    '''
    Absolute XY or homing move as: "HM,<rate>[,<position1>,<position2>]<CR>"
        See http://evil-mad.github.io/EggBot/ebb.html#HM for more information

    This is an "absolute" move, to a position relative to where the motors
    were enabled. It is not necessarily a move in a straight line.
    If both position1 and position2 are given, then move to the given position.
    Otherwise, return to the position where the motors were enabled.

    This command requires firmware version 2.6.2 or newer for moves to
    the starting position, or firmware 2.7.0 or newer for moves that
    specify an XY position.

    This command DOES NOT perform a firmware version check. Use (e.g.)
        ebb_serial.min_version(port_name, "2.6.2") or
        ebb_serial.min_version(port_name, "2.7.0") if necessary.
    '''
    if port_name is not None:
        if position1 and position2:
            str_output = 'HM,{0},{1},{2}\r'.format(rate, position1, position2)
        else:
            str_output = 'HM,{0}\r'.format(rate)
        ebb_serial.command(port_name, str_output, verbose)


def moveDistLM(rate_in, accel_in, time_ticks):
    '''
    Deprecated function as of v 0.26, and will be removed in a future version.
    Same as ebb_calc.move_dist_lt(), but does not accept or return accumulator value.
    (This function was removed because without knowing the initial accumulator value,
        it is possible to get the wrong distance.)

    Calls to this function may be replaced as per the example here, but it is better to
        use ebb_calc.move_dist_lt() *with* an initial accumulator value.
    '''
    dist, _accum = ebb_calc.move_dist_lt(rate_in, accel_in, time_ticks, 0)
    return dist


def moveDistLMA(rate_in, accel_in, time_ticks, accum_in):
    '''
    Deprecated function as of v 0.26, and will be removed in a future version.
    Function renamed to: move_dist_lt().
    '''
    return ebb_calc.move_dist_lt(rate_in, accel_in, time_ticks, accum_in)


def moveTimeLM(rate, steps, accel):
    """
    Deprecated function as of v 0.26, and will be removed in a future version.

    Calculate how long, in 40 us ISR intervals, the LM command will take to move one axis.
    Older version, for firmware 2.7+
    """

    time, _dist, _accum = ebb_calc.calculate_lm(steps, rate, accel, accum="clear")
    return time


def QueryPenUp(port_name, verbose=True):
    """ Check if the pen is up, using QP. """
    if port_name is not None:
        pen_status = ebb_serial.query(port_name, 'QP\r', verbose)
        if pen_status[0] == '0':
            return False
        return True
    return False


def QueryPRGButton(port_name, verbose=True):
    """ Check if the button has been pressed, using QB. """
    if port_name is not None:
        return ebb_serial.query(port_name, 'QB\r', verbose)
    return None

def sendDisableMotors(port_name, verbose=True):
    """ Disable stepper motors with EM command """
    if port_name is not None:
        ebb_serial.command(port_name, 'EM,0,0\r', verbose)


def sendEnableMotors(port_name, res, verbose=True):
    """
    Enable both motors with EM command at selected resolution.
        If res == 0, -> Motor disabled
        If res == 1, -> 16X microstepping
        If res == 2, -> 8X microstepping
        If res == 3, -> 4X microstepping
        If res == 4, -> 2X microstepping
        If res == 5, -> No microstepping
    """
    res = max(res, 0)
    res = min(res, 5)
    if port_name is not None:
        ebb_serial.command(port_name, 'EM,{0},{0}\r'.format(res), verbose)

def query_enable_motors(port_name, verbose=True):
    """
    Read current state of motors and their resolution.
    Returns: res_1, res_2
        These are formatted the same way as the EM command:

        If res_x == 0, -> Motor disabled
        If res_x == 1, -> 16X microstepping
        If res_x == 2, -> 8X microstepping
        If res_x == 3, -> 4X microstepping
        If res_x == 4, -> 2X microstepping
        If res_x == 5, -> No microstepping

    This query uses PI ( http://evil-mad.github.io/EggBot/ebb.html#PI )
    to read the output state of the I/O pins that control the motor driver ICs
    """
    if port_name is not None:
        try:
            result = ebb_serial.query(port_name, 'PI,E,0\r', verbose) # Read motor 1 enable pin
            enable_1 = result.split("PI,")[1].strip() == "0"
            result = ebb_serial.query(port_name, 'PI,C,1\r', verbose) # Read motor 2 enable pin
            enable_2 = result.split("PI,")[1].strip() == "0"
            result = ebb_serial.query(port_name, 'PI,E,2\r') # Read MS1
            ms_1 = result.split("PI,")[1].strip() == "1"
            result = ebb_serial.query(port_name, 'PI,E,1\r') # Read MS2
            ms_2 = result.split("PI,")[1].strip() == "1"
            result = ebb_serial.query(port_name, 'PI,A,6\r') # Read MS3
            ms_3 = result.split("PI,")[1].strip() == "1"

            if ms_1 and ms_2 and ms_3:
                res_1 = 1 # 16X microstepping
            elif ms_1 and ms_2:
                res_1 = 2 # 8X microstepping
            elif ms_2:
                res_1 = 3 # 4X microstepping
            elif ms_1:
                res_1 = 4 # 2X microstepping
            else:
                res_1 = 5 # 2X microstepping

            res_2 = res_1
            if not enable_1:
                res_1 = 0
            if not enable_2:
                res_2 = 0

            return res_1, res_2
        except:
            return None, None
    return None, None


def query_steps(port_name, verbose=True):
    """
    Read current step positions.
    Returns: steps_1, steps_2 as integers

    This query uses QS ( http://evil-mad.github.io/EggBot/ebb.html#QS )
    and requires firmware version 2.4.3 or newer.
    """

    if port_name is not None:
        try:
            result = ebb_serial.query(port_name, 'QS\r', verbose) # Query global step position
            result_list = result.strip().split(",")
            return int(result_list[0]), int(result_list[1])
        except:
            return None, None
    return None, None


def sendPenDown(port_name, pen_delay, pin=None, verbose=True):
    """
    Lower pen with SP command
    Optionally, specify which pin to use
    """
    if port_name is not None:
        if pin:
            str_output = 'SP,0,{},{}\r'.format(pen_delay, pin)
        else:
            str_output = 'SP,0,{}\r'.format(pen_delay)
        ebb_serial.command(port_name, str_output, verbose)


def sendPenUp(port_name, pen_delay, pin=None, verbose=True):
    """
    Raise pen with SP command
    Optionally, specify which pin to use
    """
    if port_name is not None:
        if pin:
            str_output = 'SP,1,{},{}\r'.format(pen_delay, pin)
        else:
            str_output = 'SP,1,{0}\r'.format(pen_delay)
        ebb_serial.command(port_name, str_output, verbose)

def PBOutConfig(port_name, pin, state, verbose=True):
    """
    Enable an I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
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


def setEBBLV(port_name, ebb_lv, verbose=True):
    """
    Set the EBB "Layer" Variable, an 8-bit number we can read and write.
    (Unrelated to document layers; name is an historical artifact.)
    """
    if port_name is not None:
        ebb_serial.command(port_name, 'SL,{0}\r'.format(ebb_lv), verbose)


def queryEBBLV(port_name, verbose=True):
    """
    Query the EBB "Layer" Variable, an 8-bit number we can read and write.
    (Unrelated to document layers; name is an historical artifact.)
    """
    if port_name is not None:
        value = ebb_serial.query(port_name, 'QL\r', verbose)
        try:
            ret_val = int(value)
            return ret_val
        except:
            return None
    return None


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


def servo_timeout(port_name, timeout_ms, state=None, verbose=True):
    """
    Set the EBB servo motor timeout.
    The EBB will cut power to the pen-lift servo motor after a given
    time delay since the last X/Y/Z motion command.
    It can also optionally set an immediate on/off state.

    The time delay timeout_ms is given in ms. A value of 0 will
    disable the automatic power-off feature.

    The state parameter is given as 0 or 1, to turn off or on
    servo power immediately, respectively.

    This feature requires EBB hardware v 2.5.0 and firmware 2.6.0

    Reference: http://evil-mad.github.io/EggBot/ebb.html#SR
    """
    if port_name is not None:
        if not ebb_serial.min_version(port_name, "2.6.0"):
            return      # Unable to read version, or version is below 2.6.0.
        if state is None:
            str_output = 'SR,{0}\r'.format(timeout_ms)
        else:
            str_output = 'SR,{0},{1}\r'.format(timeout_ms, state)
        ebb_serial.command(port_name, str_output, verbose)
