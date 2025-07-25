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

__version__ = "1.1.0"  # Dated 2025-07-23 - Replaced mpmath with decimal (it's faster)

import math
from decimal import Decimal, getcontext, ROUND_HALF_UP

# getcontext().prec = 20  # Set precision for calculations. Seems to pass with 17, keep it at 20.

# Constants used in EBB calculations
EBB_ACCUMULATOR_MAX = 2147483648  # 2^31


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
    time = int(time)
    rate = int(rate)
    accel = int(accel)

    if time == 0:
        return 0, 0

    half_accel = int(accel / 2)  # Truncates towards zero

    # Handle accumulator initialization
    if accum == "clear":
        accum = 0
        temp_rate = rate - int(accel / 2) + accel
        if temp_rate < 0:
            accum = 2147483647  # Clear to 2^31 - 1
        elif temp_rate == 0:  # Special case, if rate==0 during first step
            if accel < 0:     # Then, check rate at second step.
                accum = 2147483647
    else:
        accum = int(accum)

    # Effective rate calculation: rate + accel/2 - half_accel
    rate_effective = Decimal(rate) + Decimal(accel) / 2 - Decimal(half_accel)

    # Polynomial evaluation: accum + rate_eff*T + accel*T²/2
    accum_final = (Decimal(accum) +
                   rate_effective * Decimal(time) +
                   Decimal(accel) * Decimal(time) * Decimal(time) / 2)

    # Floor division to get steps and remainder (same as mpmath.floor)
    pos_final = int(math.floor(float(accum_final / Decimal(EBB_ACCUMULATOR_MAX))))
    accum_final_result = int(accum_final - Decimal(EBB_ACCUMULATOR_MAX) * pos_final)

    return pos_final, accum_final_result


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
    time = int(time)
    rate = int(rate)
    accel = int(accel)
    jerk = int(jerk)

    if time == 0:
        return 0, 0

    # Calculate integer divisions with proper rounding
    half_accel = int(accel / 2)  # Truncates towards zero
    jerk_over_six = int(jerk / 6)  # Truncates towards zero

    # Handle accumulator initialization
    if accum == "clear":
        accum = 0
        temp_rate = rate - half_accel + jerk_over_six + accel
        if temp_rate < 0:
            accum = 2147483647  # 2^31 - 1
        elif temp_rate == 0:
            temp_rate = accel + jerk
            if temp_rate < 0:
                accum = 2147483647
            elif temp_rate == 0:
                if jerk < 0:
                    accum = 2147483647
    else:
        accum = int(accum)

    # Pre-convert integers to Decimal to avoid redundant conversions
    rate_dec = Decimal(rate)
    accel_dec = Decimal(accel)
    jerk_dec = Decimal(jerk)
    time_dec = Decimal(time)
    accum_dec = Decimal(accum)
    half_accel_dec = Decimal(half_accel)
    jerk_over_six_dec = Decimal(jerk_over_six)

    # Pre-calculate commonly used fractions
    accel_half = accel_dec / 2
    jerk_sixth = jerk_dec / 6

    # Calculate effective rate using high-precision decimals
    # rate_effective = rate + accel/2 - half_accel + jerk_over_six - jerk/6
    rate_effective = (rate_dec + accel_half - half_accel_dec + jerk_over_six_dec - jerk_sixth)

    # Polynomial evaluation using Horner's method for efficiency
    # accum_final = accum + rate_eff*T + accel*T²/2 + jerk*T³/6
    # Horner's form: accum + T*(rate_eff + T*(accel/2 + T*(jerk/6)))
    accum_final = (accum_dec +
                   time_dec * (rate_effective +
                               time_dec * (accel_half +
                                           time_dec * jerk_sixth)))

    # Round to nearest integer (equivalent to mpmath round())
    accum_final_rounded = int(accum_final.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    # Calculate steps using floor division (same as mpmath.floor)
    pos_final = int(math.floor(accum_final_rounded / EBB_ACCUMULATOR_MAX))
    accum_final_result = accum_final_rounded - (EBB_ACCUMULATOR_MAX * pos_final)

    return int(pos_final), int(accum_final_result)


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

    return round(int(rate) - int(accel / 2) + int(jerk / 6) +
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
        return max(v_start, v_end, v_mid)

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
        return 0, 0, 0

    if accel == 0 and rate == 0:
        return 0, 0, 0

    # Handle legacy support mode
    if steps < 0:
        if rate < 0:
            return 0, 0, 0
        steps = -steps
        rate = -rate
        accel = -accel

    # Effective rate calculation
    rate_effective = Decimal(rate) + Decimal(accel) / 2 - Decimal(int(accel / 2))

    # Determine initial accumulator conditions
    initial_rate_negative = False
    temp_rate = rate - int(accel / 2) + accel
    if temp_rate < 0:
        initial_rate_negative = True
    elif temp_rate == 0:
        if accel < 0:
            initial_rate_negative = True

    if accum == "clear":
        if initial_rate_negative:
            accum = 2147483647  # 2^31 - 1
        else:
            accum = 0
    else:
        accum = int(accum)

    # Adjusted accumulator for "negative" moves
    if initial_rate_negative:
        accum_adj = accum - 2147483647
    else:
        accum_adj = accum

    # Calculate direction reversal time (if applicable)
    t_rev = -1
    if (accel != 0) and (rate != 0) and ((accel > 0) != (rate > 0)):
        t_rev_star = Decimal('0.5') - Decimal(rate) / Decimal(accel)
        t_rev = int(t_rev_star)  # Floor operation

    # Position at direction reversal
    s_rev = 0
    if t_rev > 0:
        s_rev_star = (rate_effective * Decimal(t_rev) +
                      Decimal(accel) * Decimal(t_rev) * Decimal(t_rev) / 2 +
                      Decimal(accum_adj))
        s_rev_star = abs(s_rev_star / Decimal(EBB_ACCUMULATOR_MAX))
        s_rev = int(s_rev_star)

    # Calculate final position based on direction reversal analysis
    if (t_rev <= 1) or (s_rev >= steps):
        t_rev = -1
        if initial_rate_negative:
            pos_final = -steps
        else:
            pos_final = steps
        pos_f_adj = pos_final
    elif s_rev == 0:
        if accel > 0:
            pos_final = steps
            pos_f_adj = pos_final - 1
        else:
            pos_final = -steps
            pos_f_adj = pos_final + 1
    else:
        reversed_steps = steps - s_rev
        net_steps = s_rev - reversed_steps
        if accel > 0:
            pos_final = -net_steps
            pos_f_adj = pos_final - 1
        else:
            pos_final = net_steps
            pos_f_adj = pos_final + 1

    # Calculate time using high-precision arithmetic
    if accel == 0:
        # Constant rate case: T = (2^31 * position - accumulator)/rate
        time_final_star = (Decimal(EBB_ACCUMULATOR_MAX) * Decimal(pos_final) -
                           Decimal(accum_adj)) / Decimal(rate)
    else:
        # Quadratic equation solving
        two_a = Decimal(accel)
        c_factor = Decimal(accum_adj) - Decimal(pos_f_adj) * Decimal(EBB_ACCUMULATOR_MAX)

        # Discriminant: b² - 4ac
        discriminant = rate_effective * rate_effective - 2 * two_a * c_factor

        time_final_star = Decimal(0)

        if discriminant >= 0 and two_a != 0:
            # Square root using decimal
            sq_factor = discriminant.sqrt()

            # Quadratic formula roots
            neg_root = (-rate_effective - sq_factor) / two_a
            pos_root = (-rate_effective + sq_factor) / two_a

            # Convert to integers using ceiling
            neg_root_int = math.ceil(float(neg_root)) if neg_root > 0 else -1
            pos_root_int = math.ceil(float(pos_root)) if pos_root > 0 else -1

            # Discard roots before direction change
            if (t_rev > 0) and (neg_root_int <= t_rev):
                neg_root_int = -1
            if (t_rev > 0) and (pos_root_int <= t_rev):
                pos_root_int = -1

            # Select the appropriate root
            if neg_root_int > 0:
                time_final_star = Decimal(neg_root_int)
            if pos_root_int > 0:
                if neg_root_int > 0:
                    if pos_root_int < neg_root_int:
                        time_final_star = Decimal(pos_root_int)
                else:
                    time_final_star = Decimal(pos_root_int)

    # Round up to get actual time steps
    time_final = math.ceil(float(time_final_star))

    # Calculate final accumulator value
    c_final = (Decimal(accum) +
               rate_effective * Decimal(time_final) +
               Decimal(accel) * Decimal(time_final) * Decimal(time_final) / 2)

    c_final -= Decimal(pos_final) * Decimal(EBB_ACCUMULATOR_MAX)
    c_final_result = int(c_final)

    return time_final, pos_final, c_final_result

