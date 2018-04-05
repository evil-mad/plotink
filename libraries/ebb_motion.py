# coding=utf-8
# ebb_motion.py
# Motion control utilities for EiBotBoard
# https://github.com/evil-mad/plotink
# 
# Intended to provide some common interfaces that can be used by 
# EggBot, WaterColorBot, AxiDraw, and similar machines.
#
# See version() below for version number.
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

import math

import ebb_serial
from distutils.version import LooseVersion


def version():  # Report version number for this document
    return "0.14"  # Dated March 5, 2018


def doABMove(port_name, delta_a, delta_b, duration):
    # Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>"
    # Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
    if port_name is not None:
        str_output = ','.join(['XM', str(duration), str(delta_a), str(delta_b)]) + '\r'
        ebb_serial.command(port_name, str_output)


def doTimedPause(port_name, n_pause):
    if port_name is not None:
        while n_pause > 0:
            if n_pause > 750:
                td = 750
            else:
                td = n_pause
                if td < 1:
                    td = 1  # don't allow zero-time moves
            ebb_serial.command(port_name, 'SM,' + str(td) + ',0,0\r')
            n_pause -= td


def doXYAccelMove(port_name, delta_x, delta_y, v_initial, v_final):
    # Move X/Y axes as: "AM,<initial_velocity>,<final_velocity>,<axis1>,<axis2><CR>"
    # Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
    # On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
    # Note that minimum move duration is 5 ms.
    # Important: Requires firmware version 2.4 or higher.
    if port_name is not None:
        str_output = ','.join(['AM', str(v_initial), str(v_final), str(delta_x), str(delta_y)]) + '\r'
        ebb_serial.command(port_name, str_output)


def doLowLevelMove(port_name, ri1, steps1, delta_r1, ri2, steps2, delta_r2):
    # A "pre-computed" XY movement of the form
    #  "LM,RateTerm1,AxisSteps1,DeltaR1,RateTerm2,AxisSteps2,DeltaR2<CR>"
    # See http://evil-mad.github.io/EggBot/ebb.html#LM for documentation.
    # Important: Requires firmware version 2.5.1 or higher.
    if port_name is not None:
        if (((ri1 == 0) and (delta_r1 == 0)) or (steps1 == 0)) and (((ri2 == 0) and (delta_r2 == 0)) or (steps2 == 0)):
            return
        str_output = ','.join(['LM', str(ri1), str(steps1), str(delta_r1), str(ri2), str(steps2), str(delta_r2)]) + '\r'
        ebb_serial.command(port_name, str_output)


def doXYMove(port_name, delta_x, delta_y, duration):
    # Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
    # Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
    # On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
    if port_name is not None:
        str_output = ','.join(['SM', str(duration), str(delta_y), str(delta_x)]) + '\r'
        ebb_serial.command(port_name, str_output)


def moveDistLM(rin, delta_rin, time_ticks):
    # Calculate the number of motor steps taken using the LM command,
    # with rate factor r, delta factor delta_r, and in a given number
    # of 40 us time_ticks. Calculation is for one axis only.

    # Distance moved after n time ticks is given by (n * r + (n^2 - n)*delta_r/2) / 2^31

    n = int(time_ticks)  # Ensure that the inputs are integral.
    r = int(rin)
    delta_r = int(delta_rin)

    if n == 0:
        return 0
    else:
        np = (n * n - n) >> 1  # (n^2 - n)/2 is always an integer.
        s = (n * r) + delta_r * np
        s = s >> 31
        return s


def moveTimeLM(ri, steps, delta_r):
    # Calculate how long, in 40 us ISR intervals, the LM command will take to move one axis.

    # First: Distance in steps moved after n time ticks is given by
    #  the formula: distance(time n) = (10 * r + (n^2 - n)*delta_r/2) / 2^31.
    # Use the quadratic formula to solve for possible values of n,
    # the number of time ticks needed to travel the through distance of steps.
    # As this is a floating point result, we will round down the output, and
    # then move one time step forward until we find the result.

    r = float(ri)
    d = float(delta_r)
    steps = abs(steps)  # Distance to move is absolute value of steps.

    if steps == 0:
        return 0  # No steps to take, so takes zero time.

    if delta_r == 0:
        if ri == 0:
            return 0  # No move will be made if ri and delta_r are both zero.

        # Else, case of no acceleration.
        # Simple to get actual movement time:
        # T (seconds) = (AxisSteps << 31)/(25 kHz * RateTerm)

        f = int(steps) << 31
        t = f / r
        t2 = int(math.ceil(t))
        return t2
    else:
        factor1 = (d / 2.0) - r
        factor2 = r * r - d * r + (d * d / 4.0) + (2 * d * 2147483648.0 * steps)

        if factor2 < 0:
            factor2 = 0
        factor2 = math.sqrt(factor2)
        root1 = int(math.floor((factor1 + factor2) / d))
        root2 = int(math.floor((factor1 - factor2) / d))

    if (root1 < 0) and (root2 < 0):
        return -1  # No plausible roots -- movement time must be greater than zero.

    if root1 < 0:
        time_ticks = root2  # Pick the positive root
    elif root2 < 0:
        time_ticks = root1  # Pick the positive root
    elif root2 < root1:  # If both are valid, pick the smaller value.
        time_ticks = root2
    else:
        time_ticks = root1

    # Now that we have an floor estimate for the time:
    # calculate how many steps occur in the estimated time.
    # Then, using that head start, calculate the
    # exact number of time ticks needed.

    dist = 0
    continue_loop = True
    while continue_loop:
        time_ticks += 1

        dist = moveDistLM(ri, delta_r, time_ticks)

        if (dist > 0) and (dist < steps):
            pass
        else:
            continue_loop = False

    if dist == 0:
        time_ticks = 0

    return time_ticks


def QueryPenUp(port_name):
    if port_name is not None:
        pen_status = ebb_serial.query(port_name, 'QP\r')
        if pen_status[0] == '0':
            return False
        else:
            return True


def QueryPRGButton(port_name):
    if port_name is not None:
        return ebb_serial.query(port_name, 'QB\r')


def sendDisableMotors(port_name):
    if port_name is not None:
        ebb_serial.command(port_name, 'EM,0,0\r')


def sendEnableMotors(port_name, res):
    if res < 0:
        res = 0
    if res > 5:
        res = 5
    if port_name is not None:
        ebb_serial.command(port_name, 'EM,' + str(res) + ',' + str(res) + '\r')
        # If res == 0, -> Motor disabled
        # If res == 1, -> 16X microstepping
        # If res == 2, -> 8X microstepping
        # If res == 3, -> 4X microstepping
        # If res == 4, -> 2X microstepping
        # If res == 5, -> No microstepping


def sendPenDown(port_name, pen_delay):
    if port_name is not None:
        str_output = ','.join(['SP,0', str(pen_delay)]) + '\r'
        ebb_serial.command(port_name, str_output)


def sendPenUp(port_name, pen_delay):
    if port_name is not None:
        str_output = ','.join(['SP,1', str(pen_delay)]) + '\r'
        ebb_serial.command(port_name, str_output)


def PBOutConfig(port_name, pin, state):
    # Enable an I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
    # Note that B0 is used as an alternate pause button input.
    # Note that B1 is used as the pen-lift servo motor output.
    # Note that B3 is used as the EggBot engraver output.
    # For use with a laser (or similar implement), pin 3 is recommended

    if port_name is not None:
        # Set initial Bx pin value, high or low:
        str_output = 'PO,B,' + str(pin) + ',' + str(state) + '\r'
        ebb_serial.command(port_name, str_output)
        # Configure I/O pin Bx as an output
        str_output = 'PD,B,' + str(pin) + ',0\r'
        ebb_serial.command(port_name, str_output)


def PBOutValue(port_name, pin, state):
    # Set state of the I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
    # Set the pin as an output with OutputPinBConfigure before using this.
    if port_name is not None:
        str_output = 'PO,B,' + str(pin) + ',' + str(state) + '\r'
        ebb_serial.command(port_name, str_output)


def TogglePen(port_name):
    if port_name is not None:
        ebb_serial.command(port_name, 'TP\r')


def setPenDownPos(port_name, servo_max):
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,5,' + str(servo_max) + '\r')
        # servo_max may be in the range 1 to 65535, in units of 83 ns intervals. This sets the "Pen Down" position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenDownRate(port_name, pen_down_rate):
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,12,' + str(pen_down_rate) + '\r')
        # Set the rate of change of the servo when going down.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpPos(port_name, servo_min):
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,4,' + str(servo_min) + '\r')
        # servo_min may be in the range 1 to 65535, in units of 83 ns intervals. This sets the "Pen Up" position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpRate(port_name, pen_up_rate):
    if port_name is not None:
        ebb_serial.command(port_name, 'SC,11,' + str(pen_up_rate) + '\r')
        # Set the rate of change of the servo when going up.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setEBBLV(port_name, ebb_lv):
    # Set the EBB "Layer" Variable, an 8-bit number we can read and write.
    # (Unrelated to our plot layers; name is an historical artifact.)
    if port_name is not None:
        ebb_serial.command(port_name, 'SL,' + str(ebb_lv) + '\r')


def queryEBBLV(port_name):
    # Query the EBB "Layer" Variable, an 8-bit number we can read and write.
    # (Unrelated to our plot layers; name is an historical artifact.)
    if port_name is not None:
        return int(ebb_serial.query(port_name, 'QL\r'))


def queryVoltage(port_name):
    # Query the EBB motor power supply input voltage.
    if port_name is not None:
        ebb_version_string = ebb_serial.queryVersion(port_name)  # Full string, human readable

        ebb_version_string = ebb_version_string.split("Firmware Version ", 1)

        split_len = len(ebb_version_string)
        if split_len > 1:
            ebb_version_string = ebb_version_string[1]
        else:
            return True  # We haven't received a reasonable version number response.
            # Ignore voltage test and return.
        ebb_version_string = ebb_version_string.strip()  # Stripped copy, for version # comparisons
        if ebb_version_string is not "none":
            if LooseVersion(ebb_version_string) >= LooseVersion("2.2.3"):
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
