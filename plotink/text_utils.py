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
AxiDraw, EggBot, WaterColorBot, and similar machines.
"""

def version():    # Version number for this document
    """Return version number of this script"""
    return "0.1" # Dated 2021-10-02

__version__ = version()


def format_hms (duration, milliseconds=False):
    '''
    Given a number of milliseconds or seconds, return a formatted string
    in the format:
        "12:34:56 (Hours:Minutes:Seconds)" or
        "34:56 (Minutes:Seconds)", or
        "56 Seconds", or
        "5.231 Seconds",
    depending on the duration.
    '''
    if milliseconds: # Input units are milliseconds
        m_elapsed, s_elapsed = divmod(duration/1000.0, 60)
    else: # Input units are seconds
        m_elapsed, s_elapsed = divmod(duration, 60)
    h_elapsed, m_elapsed = divmod(m_elapsed, 60)
    if h_elapsed > 0:
        out_string =  f"{int(h_elapsed)}:{int(m_elapsed):02}:{int(round(s_elapsed)):02}"
        return out_string + " (Hours, minutes, seconds)"
    if m_elapsed > 0:
        out_string =  f"{int(m_elapsed)}:{int(round(s_elapsed)):02}"
        return out_string + " (Minutes, seconds)"
    if s_elapsed >= 10:
        return f"{int(round(s_elapsed)):02} Seconds"
    return f'{s_elapsed:.3f} Seconds'


def xml_escape ( input_text ):
    '''
    Replace the five XML special characters with their character entities
    '''
    new_text = input_text.replace('&','&amp;')
    new_text = new_text.replace('<','&lt;')
    new_text = new_text.replace('>','&gt;')
    new_text = new_text.replace('"','&quot;')
    new_text = new_text.replace("'",'&apos;')
    return new_text
