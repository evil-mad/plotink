# coding=utf-8
# ebb_motion.py

"""
Motion control utilities for EiBotBoard
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by
EggBot, WaterColorBot, AxiDraw, and similar machines.

See version() below for version number.

The MIT License (MIT)

Copyright (c) 2020 Windell H. Oskay, Evil Mad Scientist Laboratories

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
"""

import math
from . import ebb_serial

def version():  # Report version number for this document
    ''' Return version number '''
    return "0.19"  # Dated October 31, 2020


def doABMove(port_name, delta_a, delta_b, duration):
    '''
    Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>"
    Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
    '''
    if port_name is not None:
        str_output = 'XM,{0},{1},{2}\r'.format(duration, delta_a, delta_b)
        ebb_serial.command(port_name, str_output)


def doTimedPause(port_name, n_pause):
    ''' "Hardware" pause on EBB control board '''
    if port_name is not None:
        while n_pause > 0:
            if n_pause > 750:
                time_delay = 750
            else:
                time_delay = n_pause
                if time_delay < 1:
                    time_delay = 1  # don't allow zero-time moves
            ebb_serial.command(port_name, 'SM,{0},0,0\r'.format(time_delay))
            n_pause -= time_delay


def doLowLevelMove(port_name, rate1, steps1, accel1, rate2, steps2, accel2, clear=None):
    '''
    Execute a "pre-computed" 2D movement of the form
      "LM,Rate1,Steps1,Accel1,Rate2,Steps2,Accel2[,Clear]<CR>"
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
        ebb_serial.command(port_name, str_output)


def doXYMove(port_name, delta_x, delta_y, duration):
    '''
    Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
    Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
    On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
    '''
    if port_name is not None:
        str_output = 'SM,{0},{1},{2}\r'.format(duration, delta_y, delta_x)
        ebb_serial.command(port_name, str_output)


def moveDistLM(rate_in, accel_in, time_ticks):
    '''
    Calculate the number of motor steps taken using the LM command,
    with rate factor r, acceleration accel_in, and in a given number
    of 40 us time_ticks. Calculation is for one axis only.
    Step distance moved after T time ticks is given by:
        S = floor(( 2 * R * T + A * T^2 )/ 2^32 )

    This calculation is valid for the revised LM command as of
    version 2.7 of the EBB firmware.
    '''
    time = int(time_ticks)  # Ensure that the inputs are integral.
    rate_r0 = int(rate_in)
    accel = int(accel_in)
    if time == 0:
        return 0
    return (2 * rate_r0 * time + accel * time * time) >> 32


def moveTimeLM(rate_in, steps, accel_in):
    """
    Calculate how long, in 40 us ISR intervals, the LM command will take to move one axis.

    First: Distance in steps moved after T time ticks is given by
      the formula: S = floor(( 2 * R * T + A * T^2 )/ 2^32 )
    Use the quadratic formula to solve for possible values of time T,
    the number of time ticks needed to travel the through distance of steps.

    As this is a floating point result, we will round down the output, and
    then move one time step forward until we find the result.

    This calculation is valid for the revised LM command as of
    version 2.7 of the EBB firmware.
    """

    steps = abs(steps)
    rate = float(rate_in)
    accel = float(accel_in)

    if steps == 0:
        return 0  # No steps to take, so takes zero time.

    if accel_in == 0:
        if rate_in == 0:
            return 0  # No move will be made if rate_in and accel_in are both zero.

        # Case of no acceleration: Simple to get actual movement time, since
        # Steps = floor(rate * Time / 2^31)
        # Thus, Time = ceil(Steps * 2^31 / rate)

        scaled_f = int(steps) << 31
        return int(math.ceil(scaled_f / rate))

    # Otherwise, accel_in is not zero.

    # Solve quadratic for T
    # S = floor(( 2 * R * T + A * T^2 )/ 2^32 )
    # -> (1/2)A T^2 + R T - 2^31 S = 0
    # a = A/2
    # b = R
    # c = -2^31 S
    #
    # T = (-b +/- sqrt(b^2 - 4 a c)) / 2 a

    # factors:
    a_fact = accel / 2.0
    b_fact = rate
    c_fact = -2147483648.0 * steps

    root_factor = b_fact * b_fact - 4 * a_fact * c_fact

    if root_factor < 0:
        root_factor = 0
    root = math.sqrt(root_factor)

    result1 = int(math.ceil((- b_fact + root) / accel))
    result2 = int(math.ceil((- b_fact - root) / accel))

    if result1 < 0 and result2 < 0:
        return -1  # No plausible roots; movement time must be positive

    if result1 < 0:
        time_ticks = result2  # Pick the positive root
    elif result2 < 0:
        time_ticks = result1  # Pick the positive root
    elif result2 < result1:  # If both are valid, pick the smaller value.
        time_ticks = result2
    else:
        time_ticks = result1
    return time_ticks


def QueryPenUp(port_name):
    """ Check if the pen is up, using QP. """
    if port_name is not None:
        pen_status = ebb_serial.query(port_name, 'QP\r')
        if pen_status[0] == '0':
            return False
        return True
    return False


def QueryPRGButton(port_name):
    """ Check if the button has been pressed, using QB. """
    if port_name is not None:
        return ebb_serial.query(port_name, 'QB\r')
    return None

def sendDisableMotors(port_name):
    """ Disable stepper motors with EM command """
    if port_name is not None:
        ebb_serial.command(port_name, 'EM,0,0\r')


def sendEnableMotors(port_name, res):
    """ Enable motors with EM command at selected resolution. """
    if res < 0:
        res = 0
    if res > 5:
        res = 5
    if port_name is not None:
        ebb_serial.command(port_name, 'EM,{0},{0}\r'.format(res))
        # If res == 0, -> Motor disabled
        # If res == 1, -> 16X microstepping
        # If res == 2, -> 8X microstepping
        # If res == 3, -> 4X microstepping
        # If res == 4, -> 2X microstepping
        # If res == 5, -> No microstepping


def sendPenDown(port_name, pen_delay):
    """ Lower pen with SP command """
    if port_name is not None:
        str_output = 'SP,0,{0}\r'.format(pen_delay)
        ebb_serial.command(port_name, str_output)


def sendPenUp(port_name, pen_delay):
    """ Raise pen with SP command """
    if port_name is not None:
        str_output = 'SP,1,{0}\r'.format(pen_delay)
        ebb_serial.command(port_name, str_output)


def PBOutConfig(port_name, pin, state):
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
        ebb_serial.command(port_name, str_output)
        # Configure I/O pin Bx as an output
        str_output = 'PD,B,{0},0\r'.format(pin)
        ebb_serial.command(port_name, str_output)


def PBOutValue(port_name, pin, state):
    """
    Set state of the I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
    Set the pin as an output with OutputPinBConfigure before using this.
    """
    if port_name is not None:
        str_output = 'PO,B,{0},{1}\r'.format(pin, state)
        ebb_serial.command(port_name, str_output)


def TogglePen(port_name):
    """ Toggle pen state using TP """
    if port_name is not None:
        ebb_serial.command(port_name, 'TP\r')


def setPenDownPos(port_name, servo_max):
    """ Set pen down position using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,5,{0}\r'.format(servo_max))
        # servo_max may be in the range 1 to 65535, in units of 83 ns intervals.
        # This sets the "Pen Down"position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenDownRate(port_name, pen_down_rate):
    """ Set pen lowering speed using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,12,{0}\r'.format(pen_down_rate))
        # Set the rate of change of the servo when going down.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpPos(port_name, servo_min):
    """ Set pen up position using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,4,{0}\r'.format(servo_min))
        # servo_min may be in the range 1 to 65535, in units of 83 ns intervals.
        # This sets the "Pen Up" position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpRate(port_name, pen_up_rate):
    """ Set pen raising speed using SC """
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,11,{0}\r'.format(pen_up_rate))
        # Set the rate of change of the servo when going up.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setEBBLV(port_name, ebb_lv):
    """
    Set the EBB "Layer" Variable, an 8-bit number we can read and write.
    (Unrelated to document layers; name is an historical artifact.)
    """
    if port_name is not None:
        ebb_serial.command(port_name, 'SL,{0}\r'.format(ebb_lv))


def queryEBBLV(port_name):
    """
    Query the EBB "Layer" Variable, an 8-bit number we can read and write.
    (Unrelated to document layers; name is an historical artifact.)
    """
    if port_name is not None:
        value = ebb_serial.query(port_name, 'QL\r')
        try:
            ret_val = int(value)
            return ret_val
        except:
            return None
    return None


def queryVoltage(port_name):
    """ Query the EBB motor power supply input voltage. """
    if port_name is not None:
        if not ebb_serial.min_version(port_name, "2.2.3"):
            return True # Unable to read version, or version is below 2.2.3.
                        # In these cases, issue no voltage warning.
        raw_string = (ebb_serial.query(port_name, 'QC\r'))
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


def servo_timeout(port_name, timeout_ms, state=None):
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
        ebb_serial.command(port_name, str_output)
