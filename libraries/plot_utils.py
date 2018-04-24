# coding=utf-8
# plot_utils.py
# Common geometric plotting utilities for EiBotBoard
# https://github.com/evil-mad/plotink
# 
# Intended to provide some common interfaces that can be used by 
# EggBot, WaterColorBot, AxiDraw, and similar machines.
#
# Version 0.10.0, Dated April 16, 2018.
#
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

from math import sqrt

import cspsubdiv
from bezmisc import beziersplitatt


def version():
    return "0.10"  # Version number for this document


PX_PER_INCH = 90.0  # 90 px per inch, as of Inkscape 0.91


# Note that the SVG specification is for 96 px per inch;
# Expect a change to 96 as of Inkscape 0.92.

def checkLimits(value, lower_bound, upper_bound):
    # Limit a value to within a range.
    # Return constrained value with error boolean.
    if value > upper_bound:
        return upper_bound, True
    if value < lower_bound:
        return lower_bound, True
    return value, False


def checkLimitsTol(value, lower_bound, upper_bound, tolerance):
    # Limit a value to within a range.
    # Return constrained value with error boolean.
    # Allow a range of tolerance where we constrain the value without an error message.

    if value > upper_bound:
        if value > (upper_bound + tolerance):
            return upper_bound, True  # Truncate & throw error
        else:
            return upper_bound, False  # Truncate with no error
    if value < lower_bound:
        if value < (lower_bound - tolerance):
            return lower_bound, True  # Truncate & throw error
        else:
            return lower_bound, False  # Truncate with no error
    return value, False  # Return original value without error


def constrainLimits(value, lower_bound, upper_bound):
    # Limit a value to within a range.
    return max(lower_bound, min(upper_bound, value))


def distance(x, y):
    '''
    Pythagorean theorem!
    '''
    return sqrt(x * x + y * y)


def dotProductXY(input_vector_first, input_vector_second):
    temp = input_vector_first[0] * input_vector_second[0] + input_vector_first[1] * input_vector_second[1]
    if temp > 1:
        return 1
    elif temp < -1:
        return -1
    else:
        return temp


def getLength(altself, name, default):
    '''
    Get the <svg> attribute with name "name" and default value "default"
    Parse the attribute into a value and associated units.  Then, accept
    no units (''), units of pixels ('px'), and units of percentage ('%').
    Return value in px.
    '''
    string_to_parse = altself.document.getroot().get(name)

    if string_to_parse:
        v, u = parseLengthWithUnits(string_to_parse)
        if not v:
            # Couldn't parse the value
            return None
        elif u == '' or u == 'px':
            return v
        elif u == 'in':
            return float(v) * PX_PER_INCH
        elif u == 'mm':
            return float(v) * PX_PER_INCH / 25.4
        elif u == 'cm':
            return float(v) * PX_PER_INCH / 2.54
        elif u == 'Q' or u == 'q':
            return float(v) * PX_PER_INCH / (40.0 * 2.54)
        elif u == 'pc':
            return float(v) * PX_PER_INCH / 6.0
        elif u == 'pt':
            return float(v) * PX_PER_INCH / 72.0
        elif u == '%':
            return float(default) * v / 100.0
        else:
            # Unsupported units
            return None
    else:
        # No width specified; assume the default value
        return float(default)


def getLengthInches(altself, name):
    '''
    Get the <svg> attribute with name "name" and default value "default"
    Parse the attribute into a value and associated units.  Then, accept
    units of inches ('in'), millimeters ('mm'), or centimeters ('cm')
    Return value in inches.
    '''
    string_to_parse = altself.document.getroot().get(name)
    if string_to_parse:
        v, u = parseLengthWithUnits(string_to_parse)
        if not v:
            # Couldn't parse the value
            return None
        elif u == 'in':
            return v
        elif u == 'mm':
            return float(v) / 25.4
        elif u == 'cm':
            return float(v) / 2.54
        elif u == 'Q' or u == 'q':
            return float(v) / (40.0 * 2.54)
        elif u == 'pc':
            return float(v) / 6.0
        elif u == 'pt':
            return float(v) / 72.0
        else:
            # Unsupported units
            return None


def parseLengthWithUnits(string_to_parse):
    '''
    Parse an SVG value which may or may not have units attached.
    There is a more general routine to consider in scour.py if more
    generality is ever needed.
    '''
    u = 'px'
    s = string_to_parse.strip()
    if s[-2:] == 'px':  # pixels, at a size of PX_PER_INCH per inch
        s = s[:-2]
    elif s[-2:] == 'in':  # inches
        s = s[:-2]
        u = 'in'
    elif s[-2:] == 'mm':  # millimeters
        s = s[:-2]
        u = 'mm'
    elif s[-2:] == 'cm':  # centimeters
        s = s[:-2]
        u = 'cm'
    elif s[-2:] == 'pt':  # points; 1pt = 1/72th of 1in
        s = s[:-2]
        u = 'pt'
    elif s[-2:] == 'pc':  # picas; 1pc = 1/6th of 1in
        s = s[:-2]
        u = 'pc'
    elif s[-1:] == 'Q' or s[-1:] == 'q':  # quarter-millimeters. 1q = 1/40th of 1cm
        s = s[:-1]
        u = 'Q'
    elif s[-1:] == '%':
        u = '%'
        s = s[:-1]

    try:
        v = float(s)
    except:
        return None, None

    return v, u


def unitsToUserUnits(input_string):
    '''
    Custom replacement for the unittouu routine in inkex.py

    Parse the attribute into a value and associated units.
    Return value in user units (typically "px").
    '''

    v, u = parseLengthWithUnits(input_string)
    if not v:
        # Couldn't parse the value
        return None
    elif u == '' or u == 'px':
        return v
    elif u == 'in':
        return float(v) * PX_PER_INCH
    elif u == 'mm':
        return float(v) * PX_PER_INCH / 25.4
    elif u == 'cm':
        return float(v) * PX_PER_INCH / 2.54
    elif u == 'Q' or u == 'q':
        return float(v) * PX_PER_INCH / (40.0 * 2.54)
    elif u == 'pc':
        return float(v) * PX_PER_INCH / 6.0
    elif u == 'pt':
        return float(v) * PX_PER_INCH / 72.0
    elif u == '%':
        return float(v) / 100.0
    else:
        # Unsupported units
        return None


def subdivideCubicPath(sp, flat, i=1):
    '''
    Break up a bezier curve into smaller curves, each of which
    is approximately a straight line within a given tolerance
    (the "smoothness" defined by [flat]).

    This is a modified version of cspsubdiv.cspsubdiv(). I rewrote the recursive
    call because it caused recursion-depth errors on complicated line segments.
    '''

    while True:
        while True:
            if i >= len(sp):
                return
            p0 = sp[i - 1][1]
            p1 = sp[i - 1][2]
            p2 = sp[i][0]
            p3 = sp[i][1]

            b = (p0, p1, p2, p3)

            if cspsubdiv.maxdist(b) > flat:
                break
            i += 1

        one, two = beziersplitatt(b, 0.5)
        sp[i - 1][2] = one[1]
        sp[i][0] = two[2]
        p = [one[2], one[3], two[1]]
        sp[i:1] = [p]


def userUnitToUnits(distance_uu, unit_string):
    '''
    Custom replacement for the uutounit routine in inkex.py

    Parse the attribute into a value and associated units.
    Return value in user units (typically "px").
    '''

    if not distance_uu:  # Couldn't parse the value
        return None
    elif unit_string == '' or unit_string == 'px':
        return distance_uu
    elif unit_string == 'in':
        return float(distance_uu) / PX_PER_INCH
    elif unit_string == 'mm':
        return float(distance_uu) / (PX_PER_INCH / 25.4)
    elif unit_string == 'cm':
        return float(distance_uu) / (PX_PER_INCH / 2.54)
    elif unit_string == 'Q' or unit_string == 'q':
        return float(distance_uu) / (PX_PER_INCH / (40.0 * 2.54))
    elif unit_string == 'pc':
        return float(distance_uu) / (PX_PER_INCH / 6.0)
    elif unit_string == 'pt':
        return float(distance_uu) / (PX_PER_INCH / 72.0)
    elif unit_string == '%':
        return float(distance_uu) * 100.0
    else:
        # Unsupported units
        return None


def vInitial_VF_A_Dx(v_final, acceleration, delta_x):
    '''
    Kinematic calculation: Maximum allowed initial velocity to arrive at distance X
    with specified final velocity, and given maximum linear acceleration.

    Calculate and return the (real) initial velocity, given an final velocity,
        acceleration rate, and distance interval.

    Uses the kinematic equation Vi^2 = Vf^2 - 2 a D_x , where
            Vf is the final velocity,
            a is the acceleration rate,
            D_x (delta x) is the distance interval, and
            Vi is the initial velocity.

    We are looking at the positive root only-- if the argument of the sqrt
        is less than zero, return -1, to indicate a failure.
    '''
    initial_v_squared = (v_final * v_final) - (2 * acceleration * delta_x)
    if initial_v_squared > 0:
        return sqrt(initial_v_squared)
    else:
        return -1


def vFinal_Vi_A_Dx(v_initial, acceleration, delta_x):
    '''
    Kinematic calculation: Final velocity with constant linear acceleration.

    Calculate and return the (real) final velocity, given an initial velocity,
        acceleration rate, and distance interval.

    Uses the kinematic equation Vf^2 = 2 a D_x + Vi^2, where
            Vf is the final velocity,
            a is the acceleration rate,
            D_x (delta x) is the distance interval, and
            Vi is the initial velocity.

    We are looking at the positive root only-- if the argument of the sqrt
        is less than zero, return -1, to indicate a failure.
    '''
    final_v_squared = (2 * acceleration * delta_x) + (v_initial * v_initial)
    if final_v_squared > 0:
        return sqrt(final_v_squared)
    else:
        return -1


def pathdata_first_point(path):
    '''
    Return the first (X,Y) point from an SVG path data string
    
    Input:  A path data string; the text of the 'd' attribute of an SVG path
    Output: Two floats in a list representing the x and y coordinates of the first point
    '''
    
    # Path origin's default values are used to see if we have
    # Written anything to the path_origin variable yet
    MaxLength = len(path)
    ix = 0
    tempString = ''
    x_val = ''
    y_val = ''
    # Check one char at a time
    # until we have the moveTo Command
    while ix < MaxLength:
        if path[ix].upper() == 'M':
            break
        # Increment until we have M
        ix = ix + 1

    # Parse path until we reach a digit, decimal point or negative sign
    while ix < MaxLength:
        if(path[ix].isdigit()) or path[ix] == '.' or path[ix] == '-':
            break
        ix = ix + 1

    # Add digits and decimal points to x_val
    # Stop parsing when next character is neither a digit nor a decimal point
    while ix < MaxLength:
        if  (path[ix].isdigit()):
            tempString = tempString + path[ix]
            x_val = float(tempString )
            ix = ix + 1
        # If next character is a decimal place, save the decimal and continue parsing
        # This allows for paths without leading zeros to be parsed correctly
        elif (path[ix] == '.' or path[ix] == '-'):
            tempString = tempString + path[ix]
            ix = ix + 1
        else:
            ix = ix + 1
            break

    # Reset tempString for y coordinate
    tempString = ''
    
    # Parse path until we reach a digit or decimal point
    while ix < MaxLength:
        if(path[ix].isdigit()) or path[ix] == '.' or path[ix] == '-':
            break
            ix = ix + 1
    
    # Add digits and decimal points to y_val
    # Stop parsin when next character is neither a digit nor a decimal point
    while ix < MaxLength:
        if (path[ix].isdigit() ):
            tempString = tempString + path[ix]
            y_val = float(tempString)
            ix = ix + 1
        # If next character is a decimal place, save the decimal and continue parsing
        # This allows for paths without leading zeros to be parsed correctly
        elif (path[ix] == '.' or path[ix] == '-'):
            tempString = tempString + path[ix]
            ix = ix + 1
        else:
            ix = ix + 1
            break
    return [x_val,y_val]


def pathdata_last_point(path):
    '''
    Return the last (X,Y) point from an SVG path data string
    
    Input:  A path data string; the text of the 'd' attribute of an SVG path
    Output: Two floats in a list representing the x and y coordinates of the last point
    
    SVG path data can be formatted in a great many ways
    This uses certain tricks to avoid deep parsing of the entire string,
    but will parse the entire string if necessary.
    
    Strings can be very large, and can be formatted such that there are good
    hints about the position (absolute moves, for example) or only 
    relative data, which would require parsing the entire string from the start.
    '''
    
    # If a path ends with a z command, the final position is the first position
    if path[-1].upper() == 'Z':
        return pathdata_first_point(path)

    # If there is no z or absolute commands, we need to parse the entire path 
    else:
        # scan path for absolute coordinates. If present, begin parsing from their index
        # instead of the beginning
        jx = 0
        x_val, y_val = 0,0    
        # Check one char at a time 
        # until we have the moveTo Command
        last_command = ''
        path_length = len(path)
        is_absolute_command = False
        repeated_command = False
        # name of command
        # how many parameters we need to skip 
        accepted_commands = {
            'M':0,
            'L':0,
            'H':0,
            'V':0,
            'C':4,
            'S':2,
            'Q':2,
            'T':0,
            'A':5
        }    
        
        # If there is an absolute command which specifies a new initial point 
        # then we can save time by setting our index directly to its location in the path data
        # See if an accepted_command is present in the path data. If it is present further in the 
        # string than any command found before, then set the pointer to that location 
        # if a command is not found, find() will return a -1. jx is initialized to 0, so if no matches
        # are found, the program will parse from the beginning to the end of the path
        
        for keys in 'MLCSQTA':
            if(path.find(keys) > jx):
                jx = path.find(keys)        

        while jx < path_length:

            temp_x_val = ''
            temp_y_val = ''
            num_of_params_to_skip = 0
            
            # SVG Path commands can be repeated 
            if (path[jx].isdigit() and last_command):
                repeated_command = True    
            else:
                repeated_command = False

            if (path[jx].isalpha() and path[jx].upper() in accepted_commands) or repeated_command:
                if repeated_command:
                    #is_relative_command is saved from last iteration of the loop
                    current_command = last_command
                else:
                    # If the character is accepted, we must parse until reach the x y coordinates
                    is_absolute_command = path[jx].isupper()    
                    current_command = path[jx].upper()

                # Each command has a certain number of parameters we must pass before we reach the
                # information we care about. We will parse until we know that we have reached them

                # Get to start of next number
                # We will know we have reached a number if the current character is a +/- sign
                # or current character is a digit 
                while jx < path_length:
                    if(path[jx] in '+-' or path[jx].isdigit()):
                        break
                    jx = jx + 1 
                        
                # We need to parse past the unused parameters in our command
                # The number of parameters to parse past is dependent on the command and stored 
                # as the value of accepted_command
                # Spaces and commas are used to deliniate paramters 
                while jx < path_length and num_of_params_to_skip < accepted_commands[current_command]:
                    if(path[jx].isspace() or path[jx] == ','):
                        num_of_params_to_skip = num_of_params_to_skip + 1 
                    jx = jx + 1 

                # Now, we are in front of the x character

                if current_command.upper() == 'V':
                    temp_x_val = 0    
                if current_command.upper() == 'H':
                    temp_y_val = 0    

                # Parse until next character is a digit or +/- character
                while jx < path_length and current_command.upper() != 'V':
                    if(path[jx] in '+-' or path[jx].isdigit()):
                        break
                    jx = jx + 1 
                
                # Save each next character until we reach a space
                while jx < path_length and current_command.upper() != 'V' and not (path[jx].isspace() or path[jx] == ','):
                    temp_x_val = temp_x_val + path[jx]
                    jx = jx + 1 
                # Then we know we have completely parsed the x character

                # Now we are in front of the y character
                # Parse until next character is a digit or +/- character
                while jx < path_length and current_command.upper() != 'H':
                    if(path[jx] in '+-' or path[jx].isdigit()):
                        break
                    jx = jx + 1 

                # Save each next character until we reach a space
                while jx < path_length and current_command.upper() != 'H' and not (path[jx].isspace() or path[jx] == ','):
                    temp_y_val = temp_y_val + path[jx]
                    jx = jx + 1 
                # Then we know we have completely parsed the y character

                if is_absolute_command:

                    if current_command == 'H':
                        # Absolute commands create new x,y position 
                        try:
                            x_val = float(temp_x_val)
                        except ValueError:
                            pass
                    elif current_command == 'V':
                        # Absolute commands create new x,y position 
                        try:
                            y_val = float(temp_y_val)
                        except ValueError:
                            pass
                    else:
                        # Absolute commands create new x,y position 
                        try:
                            x_val = float(temp_x_val)
                            y_val = float(temp_y_val)
                        except ValueError:
                            pass
                else:
                    if current_command == 'h':
                        # Absolute commands create new x,y position 
                        try:
                            x_val = x_val + float(temp_x_val)
                        except ValueError:
                            pass
                    elif current_command == 'V':
                        # Absolute commands create new x,y position 
                        try:
                            y_val = y_val + float(temp_y_val)
                        except ValueError:
                            pass
                    else:
                        # Absolute commands create new x,y position 
                        try:
                            x_val = x_val + float(temp_x_val)
                            y_val = y_val + float(temp_y_val)
                        except ValueError:
                            pass
                last_command = current_command
            jx = jx + 1
        return [x_val,y_val]