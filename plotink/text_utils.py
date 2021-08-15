# -*- coding: utf-8 -*-
# text_utils.py
# Common text processing utilities
# https://github.com/evil-mad/plotink
#
# See below for version information
#
# Copyright (c) 2021 Windell H. Oskay, Evil Mad Scientist Laboratories
#
# The MIT License (MIT)
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

"""
text_utils.py

Common text processing utilities
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by
EggBot, WaterColorBot, AxiDraw, and similar machines.
"""

def version():    # Version number for this document
    """Return version number of this script"""
    return "0.1" # Dated 2021-08-15

__version__ = version()


def format_hms ( duration, seconds=False ):
    '''
    Given a number of milliseconds or seconds, return a formatted string
    in the format "12:34:56 (Hours:Minutes:Seconds)" or
    "34:56 (Minutes:Seconds)", depending on whether the time is
    greater or less than one hour.
    '''
    if seconds:
        m_elapsed, s_elapsed = divmod(duration, 60)
    else: # Input units are milliseconds
        m_elapsed, s_elapsed = divmod(duration/1000.0, 60)
    h_elapsed, m_elapsed = divmod(m_elapsed, 60)
    if h_elapsed > 0:
        out_string =  f"{int(h_elapsed)}:{int(m_elapsed):02}:{int(s_elapsed):02}"
        return out_string + " (Hours, minutes, seconds)"
    out_string =  f"{int(m_elapsed)}:{int(s_elapsed):02}"
    return out_string + " (Minutes, seconds)"


def position_scale (x_value, y_value, units_code):
    '''
    Format position data to be returned to user
    x_value, y_value inputs are in inches.
    Output set by units_code: 1 for cm, 2 for mm, 0 (or otherwise) for inch.
    '''
    if units_code == 1 : # If using centimeter units
        x_value = x_value * 2.54
        y_value = y_value * 2.54
    if units_code == 2: # If using millimeter units
        x_value = x_value * 25.4
        y_value = y_value * 25.4
    return x_value, y_value
