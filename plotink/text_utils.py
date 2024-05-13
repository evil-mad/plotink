'''
 text_utils.py

Common text processing utilities

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

def version():    # Version number for this document
    """Return version number of this script"""
    return "0.2.1" # Dated 2024-05-13

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
    Times greater than or equal to 10 s are rounded to the nearest second.
    '''
    if milliseconds: # Input units are milliseconds
        duration = duration / 1000.0
    if duration < 10:
        return f'{duration:.3f} Seconds'
    duration_rounded = int(round(duration))
    if duration_rounded < 60:
        return f"{int(round(duration_rounded)):02} Seconds"
    m_elapsed, s_elapsed = divmod(duration_rounded, 60)
    if duration_rounded < 3600:
        out_string =  f"{int(m_elapsed)}:{int(s_elapsed):02}"
        return out_string + " (Minutes, seconds)"
    h_elapsed, m_elapsed = divmod(m_elapsed, 60)
    out_string =  f"{int(h_elapsed)}:{int(m_elapsed):02}:{int(s_elapsed):02}"
    return out_string + " (Hours, minutes, seconds)"


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
