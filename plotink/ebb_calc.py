'''
ebb_calc.py

Motion control calculations for EiBotBoard


Part of the plotink plotting utilities for use with EiBotBoard
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

__version__ = "1.0.1"  # Dated 2024-05-13

import math
import mpmath

def version():  # Report version number for this document
    ''' Return version number '''
    return __version__

def move_dist_lt(rate, accel, time, accum="clear"):
    '''
    Calculate motor step count and final accumulator value after a given number
    of ISR time ticks, using the LM or LT command. Calculation is for one axis only.

    Inputs: Rate factor rate, acceleration accel, 
            number of 40 us intervals time,
            initial accumulator value (Default: "clear", or integer)

    Accumulator value at T time ticks is given by:
        Accum = R_eff * T + 0.5 * accel_in * T^2 + accum_in
        Steps = floor (Accum / 2^31)
        Remainder = Accum - 2^31 * Steps

    Return Step position, Final accumulator value
    This calculation is valid for version 2.7+ of the EBB firmware.
    '''
    time = int(time)  # Ensure that the inputs are integer.
    rate = int(rate)
    accel = int(accel)
    if time == 0:
        return 0, 0

    mpmath.mp.dps = 30 # Set decimal precision of 30.

    half_accel = int(accel / 2) # Rounds towards zero

    if accum == "clear": # Clear accumulator!
        accum = 0       # Clear to zero
        temp_rate = rate - int(accel / 2) + accel # Rate at step 1, as first added to accumulator
        if temp_rate < 0:
            accum = 2147483647  # Clear to 2^31 - 1
        elif temp_rate == 0:                    # Special case, if rate==0 during first step
            if accel < 0:           # Then, check rate at second step.
                accum = 2147483647  # Clear to 2^31 - 1
    else:
        accum = int(accum)

    # Account for difference in effective rate due to rounding of accel/2:
    rate_effective = rate + mpmath.mpf(accel) / 2 - half_accel

    # Total accumulator value at end of move, if it were not restricted to in [0, 2^31):
    accum_final = mpmath.mpf(accum) + rate_effective * time +\
                mpmath.mpf(accel) * time * time / 2

    pos_final = mpmath.floor(accum_final / mpmath.mpf(2147483648)) # Divide by 2^31 to get steps
    accum_final -= 2147483648 * mpmath.mpf(pos_final)

    return int(pos_final), int(accum_final)


def move_dist_t3(time, rate, accel, jerk, accum="clear"):
    '''
    Calculate final motor step count and accumulator value after a given number
    of ISR time ticks, using the T3 command. Calculation is for one axis only.

    Inputs: Number of 40 us intervals time, initial rate, accel, jerk,
            initial accumulator value (Default: "clear", or integer)

    Accumulator value at T time ticks is given by:
        Accum = R_eff * T + 0.5 * accel * T^2 + accum + jerk * T^3 /6
        Steps = floor(Accum / 2^31)
        Remainder = Accum - 2^31 * Steps

    Return Step position, Final accumulator value
    This calculation is valid for version 3.0+ of the EBB firmware.
    '''
    time = int(time)  # Ensure that the inputs are integer.
    rate = int(rate)
    accel = int(accel)
    jerk = int(jerk)
    if time == 0:
        return 0, 0

    mpmath.mp.dps = 30 # Set decimal precision of 30.

    half_accel = int(accel / 2) # Rounds towards zero
    jerk_over_six = int(jerk / 6) # Rounds towards zero

    if accum == "clear": # Clear accumulator!
        accum = 0       # Clear to zero
        temp_rate = rate - half_accel + jerk_over_six + accel
        if temp_rate < 0:  # Rate at step 1, as first added to accumulator, is < 0.
            accum = 2147483647  # Clear to 2^31 - 1
        elif temp_rate == 0:            # Special case: rate==0 during 1st step
            temp_rate = accel + jerk        # Rate at step 2 (if rate at step 1 is zero)
            if temp_rate < 0:               # If the new rate < 0...
                accum = 2147483647          # Clear to 2^31 - 1
            elif temp_rate == 0:        # Special case: rate==0 during 2nd step too!
                if jerk < 0:                # If the rate at the 3rd step is < 0...
                    accum = 2147483647      # Clear to 2^31 - 1
    else:
        accum = int(accum)

    # Account for difference in effective rate due to rounding of accel/2 - jerk/6:
    rate_effective = rate + mpmath.mpf(accel)/2 - half_accel +\
                        jerk_over_six - mpmath.mpf(jerk)/6

    if abs(rate_effective - mpmath.mpf(rate)) < 0.01:
        rate_effective = rate # Use integer value for cases where we can

    # Total accumulator value at end of move, if it were not restricted to in [0, 2^31):
    accum_final = mpmath.mpf(accum) + rate_effective * time +\
                    mpmath.mpf(accel) * time * time / 2 +\
                    mpmath.mpf(jerk) * time * time * time / 6
    accum_final = round(accum_final) # Find nearest integer value


    pos_final = mpmath.floor(accum_final / mpmath.mpf(2147483648)) # Divide by 2^31 to get steps
    accum_final -= 2147483648 * mpmath.mpf(pos_final)

    return int(pos_final), int(accum_final)


def rate_t3(time, rate, accel, jerk):
    '''
    Calculate final rate after a T3 command, for one axis.

    Inputs: number of 40 us intervals time, initial rate, accel, jerk

    Return rate value at T time ticks, given approximately by:
        Rate = Rate_initial + accel * T + accum + jerk * T^2 /2
        Some fine-tuned corrections give the actual value.

    Note on time convention: A move will always be at least one interval long;
        the rate after one interval is given when time T = 1. A rate after
        zero intervals (T=0) would be the theoretical value of the rate
        *before* the T3 move begins.

    Rate should never be allowed to exceed 2^31 - 1 ( 2147483647 ).
    '''
    time = int(time)  # Use "ints" to ensure that the inputs are integer.

    if time == 0:
        return rate + accel + jerk

    return round(int(rate) - int(accel / 2) + int(jerk / 6) +\
                (int(accel) - jerk/2) * time + jerk * time * time / 2)


def max_rate_t3(time, rate, accel, jerk):
    '''
    Calculate maximum rate during a T3 command, for one axis.
    Inputs: number of 40 us intervals time, initial rate, accel, jerk
    Return absolute value of maximum rate.

    Discrete time approach gives R(T) = r_e + a_e T + J (T^2 + T)/2,
        with effective rate r_e = rate - int(accel/2) + int(jerk/6)
            effective accel a_e = accel - jerk
    Set derivative equal to zero, to find time where min/max occurs:
        R'(T) = 0 = 0 + a_e + (J/2)(2T + 1) = A - J + JT + J/2 = A - J/2 + JT
        -> T = (J/2 - A)/J

    Rate should not exceed 2^31 - 1 ( 2147483647 ).
    '''
    time = int(time)  # Ensure that the inputs are integer.
    v_start = abs(rate_t3(1, rate, accel, jerk))
    if time <= 1:
        return v_start
    v_end = abs(rate_t3(time, rate, accel, jerk))

    if jerk == 0:
        return max(v_start, v_end)

    t_mid = (jerk/2 - accel) / jerk

    if 1.5 < t_mid < (time - 1.5):
        v_mid = abs(rate_t3(math.ceil(t_mid), rate, accel, jerk))
        return max(v_start, v_end ,v_mid)

    return max(v_start, v_end)


def calculate_lm(steps, rate, accel, accum="clear"):
    """
    Calculate final distance, time, and accumulator for an LM command move.
    Inputs: step count (integer),  initial rate (integer), acceleration (integer),
        initial accumulator value (Default: "clear", or integer)

    Returns: Duration of movement (integer, in 40 us ISR interval units), 
        move distance (integer), final accumulator value (integer).
        For invalid moves, returns 0, 0, 0.

    This calculation is valid for the revised LM command as of
    version 3.0 of the EBB firmware, handling new cases of moves that reverse direction.

    For legacy support, negative step count gives: steps = -steps, rate = -rate, accel = -accel
        negative input rate is not supported with a negative step count.
    """

    steps = int(steps)
    rate = int(rate)
    accel = int(accel)

    if steps == 0:
        return 0, 0, 0  # No steps to take; exit.

    if accel == 0 and rate == 0:
        return 0, 0, 0  # No move will be made if rate and accel are both zero.

    if steps < 0:   # Legacy support mode
        if rate < 0: # Negative initial rate not supported in legacy support mode.
            return 0, 0, 0
        steps = -steps
        rate = -rate
        accel = -accel

    mpmath.mp.dps = 30 # Set decimal precision of 30.

    # Account for difference in effective rate due to rounding of accel/2:
    rate_effective = rate + mpmath.mpf(accel) / 2 - int(accel/2)

    initial_rate_negative = False
    temp_rate = rate - int(accel / 2) + accel # Rate at step 1, as first added to accumulator
    if temp_rate < 0:
        initial_rate_negative = True
    elif temp_rate == 0:                    # Special case, if rate==0 during first step
        if accel < 0:                       # Then, check rate at second step.
            initial_rate_negative = True

    if accum == "clear": # Clear accumulator!
        if initial_rate_negative:
            accum = 2147483647 # 2^31 - 1
        else:
            accum = 0
    else:
        accum = int(accum) # Accept only integer, if not clearing

    if initial_rate_negative: # Adjusted accumulator value for "negative" moves
        accum_adj = accum - 2147483647 # 2^31 - 1
    else:
        accum_adj = accum

    # Calculate time when motion reverses direction of rotation, if it does so.
    # Begin with initial assumption that motor does not reverse direction: flag as t = -1.
    t_rev_star = -1.0   # Time, float, when rate = 0; i.e., when motor direction reverses
    t_rev = -1          # Integer timestep of last motor step in initial motion direction
    if (accel != 0) and (rate != 0) and ((accel > 0) != (rate > 0)):
        t_rev_star = 0.5 - rate / accel
        t_rev = math.floor(t_rev_star)

    s_rev = 0 # Position at direction reversal: S_Rev = (R0 T + 1/2A T^2 + C0) / 2^31
    if t_rev > 0:
        s_rev_star = rate_effective * t_rev + \
            mpmath.mpf('0.5') * accel * t_rev * t_rev + accum_adj

        s_rev_star = mpmath.fabs(s_rev_star / 2147483648) # divide by 2^31
        s_rev = int(mpmath.floor(s_rev_star))

    # Calculate final position. And, adjusted final position, with step position rounded
    #   "back" by 1, in cases where direction reverses. This correction means that we look
    #   for the *first* time step at the target position, not the *last*.
    if (t_rev <= 1) or (s_rev >= steps): # Reversal by first step or after end of move
        t_rev = -1 # Set flag: No direction reversal during this move.
        if initial_rate_negative:
            pos_final = -steps
        else:
            pos_final = steps
        pos_f_adj = pos_final
    elif s_rev == 0: # Case: Rate reverses direction at t>=1 but *before* first motor step.
        if accel > 0: # All motor steps have same sign as accel
            pos_final = steps
            pos_f_adj = pos_final - 1
        else:
            pos_final = -1 * steps
            pos_f_adj = pos_final + 1
    else: # Case: At least one motor step is made in each direction.
        reversed_steps = steps - s_rev # "forward" step count at reversal is given by s_rev.
        net_steps = s_rev - reversed_steps # i.e., net_steps = 2 * s_rev - steps_in
        if accel > 0: # Motion began negative, reversed with positive acceleration
            pos_final = -net_steps
            pos_f_adj = pos_final - 1
        else:
            pos_final = net_steps
            pos_f_adj = pos_final + 1

    # Case of no acceleration; constant rate: T = (2^31 * position - accumulator)/rate
    if accel == 0:
        time_final_star = (2147483648 * pos_final - mpmath.mpf(accum_adj))/mpmath.mpf(rate)
    else:   # Begin time calculation for moves with acceleration.
        # Method: Solve quadratic for T
        # Final accumulator value C* = ( C_0 + R_eff * T + A * T^2/2 )
        # -> T = (-b +/- sqrt(b^2 - 4 a c)) / 2 a,
        #   with a = accel/2, b = effective rate, C = C_0 - pos_f_adj * @^31

        time_final_star = 0 # Fallback, if no solutions are found.
        two_a = mpmath.mpf(accel) # 2 * a = 2 * accel/2
        c_factor = accum_adj - mpmath.mpf(pos_f_adj) * 2147483648
        discriminant = rate_effective * rate_effective - 2 * two_a * c_factor # b^2 - 4 a c

        neg_root = -1
        pos_root = -1
        time_final = -1

        # Roots must be positive and real, and not lead to a solution
        #   before the direction change, if there is a direction change.
        if (discriminant >= 0) and (two_a != 0):
            sq_factor = mpmath.sqrt(discriminant)
            neg_root = (-rate_effective - sq_factor ) / two_a
            pos_root = (-rate_effective + sq_factor ) / two_a

            pos_root = mpmath.ceil(pos_root)
            neg_root = mpmath.ceil(neg_root)

            # For moves that reverse direction, discard root before direction change.
            if (t_rev > 0) and (neg_root <= t_rev):
                neg_root = -1
            if (t_rev > 0) and (pos_root <= t_rev):
                pos_root = -1

        # If two remaining possible roots (same position at two times), pick the first.
        if neg_root > 0:
            time_final_star = neg_root
        if pos_root > 0:
            if neg_root > 0:
                if pos_root < neg_root:
                    time_final_star = pos_root
            else:
                time_final_star = pos_root

    time_final = int(mpmath.ceil(time_final_star)) # Round up to get actual time steps.

    # Total accumulator value at end of move, if it were not restricted to in  [0, 2^31):
    c_final = mpmath.mpf(accum) + rate_effective * time_final +\
                mpmath.mpf(accel) * time_final * time_final / 2

    c_final -= 2147483648 * mpmath.mpf(pos_final)

    return time_final, pos_final, int(c_final)
