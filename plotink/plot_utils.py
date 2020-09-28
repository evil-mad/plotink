# -*- coding: utf-8 -*-
# plot_utils.py
# Common plotting utilities
# https://github.com/evil-mad/plotink
#
# See below for version information
#
# Copyright (c) 2020 Windell H. Oskay, Evil Mad Scientist Laboratories
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
plot_utils.py

Common plotting utilities
https://github.com/evil-mad/plotink

Intended to provide some common interfaces that can be used by
EggBot, WaterColorBot, AxiDraw, and similar machines.
"""

from math import sqrt, isclose

from .plot_utils_import import from_dependency_import
cspsubdiv = from_dependency_import('ink_extensions.cspsubdiv')
simplepath = from_dependency_import('ink_extensions.simplepath')
bezmisc = from_dependency_import('ink_extensions.bezmisc')
ffgeom = from_dependency_import('ink_extensions.ffgeom')

def version():    # Version number for this document
    """Return version number of this script"""
    return "0.18" # Dated 2020-09-29

__version__ = version()

PX_PER_INCH = 96.0
# This value has changed to 96 px per inch, as of version 0.12 of this library.
# Prior versions used 90 PPI, corresponding the value used in Inkscape < 0.92.
# For use with Inkscape 0.91 (or older), use PX_PER_INCH = 90.0

trivial_svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg
       xmlns:dc="http://purl.org/dc/elements/1.1/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:svg="http://www.w3.org/2000/svg"
       xmlns="http://www.w3.org/2000/svg"
       version="1.1"
       id="svg15158"
       viewBox="0 0 297 210"
       height="210mm"
       width="297mm">
    </svg>
    """

def checkLimits(value, lower_bound, upper_bound):
    """
    Limit a value to within a range.
    Return constrained value with error boolean.
    """
    if value > upper_bound:
        return upper_bound, True
    if value < lower_bound:
        return lower_bound, True
    return value, False


def checkLimitsTol(value, lower_bound, upper_bound, tolerance):
    """
    Limit a value to within a range.
    Return constrained value with error boolean.
    Allow a range of tolerance where we constrain the value without an error message.
    """
    if value > upper_bound:
        if value > (upper_bound + tolerance):
            return upper_bound, True  # Truncate & throw error
        return upper_bound, False  # Truncate with no error
    if value < lower_bound:
        if value < (lower_bound - tolerance):
            return lower_bound, True  # Truncate & throw error
        return lower_bound, False  # Truncate with no error
    return value, False  # Return original value without error


def clip_code(x_in, y_in, x_min, x_max, y_min, y_max):
    """Encode point position with respect to boundary box"""
    code = 0
    if x_in < x_min:
        code = 1  # Left
    if x_in > x_max:
        code |= 2 # Right
    if y_in < y_min:
        code |= 4 # Top
    if y_in > y_max:
        code |= 8 # Bottom
    return code


def clip_segment(segment, bounds):
    """
    Given an input line segment [[x_1, y_1], [x_2, y_2]], as well as a
    rectangular bounding region [[x_min, y_min], [x_max, y_max]], clip and
    keep the part of the segment within the bounding region, using the
    Cohen–Sutherland algorithm.
    Return a boolean value, "accept", indicating that the output
    segment is non-empty, as well as truncated segment,
    [[x_1', y_1'], [x_2', y_2']], giving the portion of the input line segment
    that fits within the bounds.
    """

    x_1 = segment[0][0]
    y_1 = segment[0][1]
    x_2 = segment[1][0]
    y_2 = segment[1][1]

    x_min = bounds[0][0]
    y_min = bounds[0][1]
    x_max = bounds[1][0]
    y_max = bounds[1][1]

    while True: # Repeat until return
        code_1 = clip_code(x_1, y_1, x_min, x_max, y_min, y_max)
        code_2 = clip_code(x_2, y_2, x_min, x_max, y_min, y_max)

        # Trivial accept:
        if code_1 == 0 and code_2 == 0:
            return True, segment # Both endpoints are within bounds.
        # Trivial reject, if both endpoints are outside, and on the same side:
        if code_1 & code_2:
            return False, segment # Verify with bitwise AND.

        # Otherwise, at least one point is out of bounds; not trivial.
        if code_1 != 0:
            code = code_1
        else:
            code = code_2

        # Clip at a single boundary; may need to do this up to twice per vertex

        if code & 1: # Vertex on LEFT side of bounds:
            x_new = x_min  # Find intersection of our segment with x_min
            slope = (y_2 - y_1) / (x_2 - x_1)
            y_new = slope * (x_min - x_1) + y_1

        elif code & 2:  # Vertex on RIGHT side of bounds:
            x_new = x_max # Find intersection of our segment with x_max
            slope = (y_2 - y_1) / (x_2 - x_1)
            y_new = slope * (x_max - x_1) + y_1

        elif code & 4: # Vertex on TOP side of bounds:
            y_new = y_min  # Find intersection of our segment with y_min
            slope = (x_2 - x_1) / (y_2 - y_1)
            x_new = slope * (y_min - y_1) + x_1

        elif code & 8: # Vertex on BOTTOM side of bounds:
            y_new = y_max  # Find intersection of our segment with y_max
            slope = (x_2 - x_1) / (y_2 - y_1)
            x_new = slope * (y_max - y_1) + x_1

        if code == code_1:
            x_1 = x_new
            y_1 = y_new
        else:
            x_2 = x_new
            y_2 = y_new
        segment = [[x_1, y_1], [x_2, y_2]] # Now checking this clipped segment


def constrainLimits(value, lower_bound, upper_bound):
    """ Limit a value to within a range. """
    return max(lower_bound, min(upper_bound, value))


def distance(x_in, y_in):
    """
    Pythagorean theorem
    """
    return sqrt(x_in * x_in + y_in * y_in)


def dotProductXY(input_vector_first, input_vector_second):
    """Dot product of vectors"""
    temp = input_vector_first[0] * input_vector_second[0] +\
                    input_vector_first[1] * input_vector_second[1]
    if temp > 1:
        return 1
    if temp < -1:
        return -1
    return temp


def getLength(altself, name, default):
    """
    Get the <svg> attribute with name "name" and default value "default"
    Parse the attribute into a value and associated units.  Then, accept
    no units (''), units of pixels ('px'), and units of percentage ('%').
    Return value in px.
    """
    string_to_parse = altself.document.getroot().get(name)

    if string_to_parse:
        value, unit = parseLengthWithUnits(string_to_parse)
        if value is None:
            return None
        if unit in ('', 'px'):
            return float(value)
        if unit == 'in':
            return float(value) * PX_PER_INCH
        if unit == 'mm':
            return float(value) * PX_PER_INCH / 25.4
        if unit == 'cm':
            return float(value) * PX_PER_INCH / 2.54
        if unit in ('Q', 'q'):
            return float(value) * PX_PER_INCH / (40.0 * 2.54)
        if unit == 'pc':
            return float(value) * PX_PER_INCH / 6.0
        if unit == 'pt':
            return float(value) * PX_PER_INCH / 72.0
        if unit == '%':
            return float(default) * value / 100.0
        # Unsupported units
        return None
    # No width specified; assume the default value
    return float(default)


def getLengthInches(altself, name):
    """
    Get the <svg> attribute with name "name", and parse it as a length,
    into a value and associated units. Return value in inches.

    As of version 0.11, units of 'px' or no units ('') are interpreted
    as imported px, at a resolution of 96 px per inch, as per the SVG
    specification. (Prior versions returned None in this case.)

    This allows certain imported SVG files, (imported with units of px)
    to plot while they would not previously. However, it may also cause
    new scaling issues in some circumstances. Note, for example, that
    Adobe Illustrator uses 72 px per inch, and Inkscape used 90 px per
    inch prior to version 0.92.
    """
    string_to_parse = altself.document.getroot().get(name)
    if string_to_parse:
        value, unit = parseLengthWithUnits(string_to_parse)
        if value is None:
            return None
        if unit == 'in':
            return float(value)
        if unit == 'mm':
            return float(value) / 25.4
        if unit == 'cm':
            return float(value) / 2.54
        if unit in ('Q', 'q'):
            return float(value) / (40.0 * 2.54)
        if unit == 'pc':
            return float(value) / 6.0
        if unit == 'pt':
            return float(value) / 72.0
        if unit in ('', 'px'):
            return float(value) / 96.0
    # Unsupported units (including '%') or no string to parse:
    return None


def parseLengthWithUnits(string_to_parse):
    """
    Parse an SVG value which may or may not have units attached.
    There is a more general routine to consider in scour.py if more
    generality is ever needed.
    """
    units = 'px'
    string = string_to_parse.strip()
    if string[-2:] == 'px':  # pixels, at a size of PX_PER_INCH per inch
        string = string[:-2]
    elif string[-2:] == 'in':  # inches
        string = string[:-2]
        units = 'in'
    elif string[-2:] == 'mm':  # millimeters
        string = string[:-2]
        units = 'mm'
    elif string[-2:] == 'cm':  # centimeters
        string = string[:-2]
        units = 'cm'
    elif string[-2:] == 'pt':  # points; 1pt = 1/72th of 1in
        string = string[:-2]
        units = 'pt'
    elif string[-2:] == 'pc':  # picas; 1pc = 1/6th of 1in
        string = string[:-2]
        units = 'pc'
    elif string[-1:] == 'Q' or string[-1:] == 'q':  # quarter-millimeters. 1q = 1/40th of 1cm
        string = string[:-1]
        units = 'Q'
    elif string[-1:] == '%':
        units = '%'
        string = string[:-1]

    try:
        value = float(string)
    except ValueError:
        return None, None

    return value, units


def unitsToUserUnits(input_string):
    """
    Custom replacement for the unittouu routine in inkex.py

    Parse the attribute into a value and associated units.
    Return value in user units (typically "px").
    """

    value, unit = parseLengthWithUnits(input_string)
    if value is None:
        return None
    if unit in ('', 'px'):
        return float(value)
    if unit == 'in':
        return float(value) * PX_PER_INCH
    if unit == 'mm':
        return float(value) * PX_PER_INCH / 25.4
    if unit == 'cm':
        return float(value) * PX_PER_INCH / 2.54
    if unit in ('Q', 'q'):
        return float(value) * PX_PER_INCH / (40.0 * 2.54)
    if unit == 'pc':
        return float(value) * PX_PER_INCH / 6.0
    if unit == 'pt':
        return float(value) * PX_PER_INCH / 72.0
    if unit == '%':
        return float(value) / 100.0
    # Unsupported units
    return None


def subdivideCubicPath(s_p, flat, i=1):
    """
    Break up a bezier curve into smaller curves, each of which
    is approximately a straight line within a given tolerance
    (the "smoothness" defined by [flat]).

    This is a modified version of cspsubdiv.cspsubdiv(). I rewrote the recursive
    call because it caused recursion-depth errors on complicated line segments.
    """

    while True:
        while True:
            if i >= len(s_p):
                return
            p_0 = s_p[i - 1][1]
            p_1 = s_p[i - 1][2]
            p_2 = s_p[i][0]
            p_3 = s_p[i][1]

            b_list = (p_0, p_1, p_2, p_3)

            if cspsubdiv.maxdist(b_list) > flat:
                break
            i += 1

        one, two = bezmisc.beziersplitatt(b_list, 0.5)
        s_p[i - 1][2] = one[1]
        s_p[i][0] = two[2]
        p_list = [one[2], one[3], two[1]]
        s_p[i:1] = [p_list]


def max_dist_from_n_points(input_points):
    """
    Like cspsubdiv.maxdist, but it can check for distances of any number of points >= 0.

    `input_points` is an ordered collection of xy vertices.
    The first point and the last point define the segment we are finding distances from.

    does not mutate `input_points`
    """
    assert len(input_points) >= 3, "There must be points (other than begin/end) to check."

    points = [ffgeom.Point(point[0], point[1]) for point in input_points]
    segment = ffgeom.Segment(points.pop(0), points.pop())

    distances = [segment.distanceToPoint(point) for point in points]
    return max(distances)


def supersample(vertices, tolerance):
    """
    Given a list of vertices, remove some according to the following algorithm.

    Suppose that the vertex list consists of points A, B, C, D, E, and so forth,
    which define segments AB, BC, CD, DE, EF, and so on.

    We first test to see if vertex B can be removed, by using perpDistanceToPoint
    to check whether the distance between B and segment AC is less than tolerance.

    If B can be removed, then check to see if the next vertex, C, can be removed.
    Both B and C can be removed if the both the distance between B and AD is less
    than Tolerance and the distance between C and AD is less than Tolerance. Continue
    removing additional vertices, so long as the perpendicular distance between every
    point removed and the resulting segment is less than tolerance (and the end of the
    vertex list is not reached).

    If B cannot be removed, then move onto vertex C, and perform the same checks,
    until the end of the vertex list is reached.
    """
    if len(vertices) <= 2: # there is nothing to delete
        return vertices

    start_index = 0 # can't remove first vertex
    while start_index < len(vertices) - 2:
        end_index = start_index + 2
        # test the removal of (start_index, end_index), exclusive until we can't advance end_index
        while (max_dist_from_n_points(vertices[start_index:end_index + 1]) < tolerance
               and end_index < len(vertices)):
            end_index += 1 # try removing the next vertex too

        vertices[start_index + 1:end_index - 1] = [] # delete (start_index, end_index), exclusive
        start_index += 1

def userUnitToUnits(distance_uu, unit_string):
    """
    Custom replacement for the uutounit routine in inkex.py

    Parse the attribute into a value and associated units.
    Return value in user units (typically "px").
    """

    if distance_uu is None:  # Couldn't parse the value
        return None
    if unit_string in ('', 'px'):
        return float(distance_uu)
    if unit_string == 'in':
        return float(distance_uu) / PX_PER_INCH
    if unit_string == 'mm':
        return float(distance_uu) / (PX_PER_INCH / 25.4)
    if unit_string == 'cm':
        return float(distance_uu) / (PX_PER_INCH / 2.54)
    if unit_string in ('Q', 'q'):
        return float(distance_uu) / (PX_PER_INCH / (40.0 * 2.54))
    if unit_string == 'pc':
        return float(distance_uu) / (PX_PER_INCH / 6.0)
    if unit_string == 'pt':
        return float(distance_uu) / (PX_PER_INCH / 72.0)
    if unit_string == '%':
        return float(distance_uu) * 100.0
    # Unsupported units
    return None


def vb_scale(v_b, p_a_r, doc_width, doc_height):
    """"
    Parse SVG viewbox and generate scaling parameters.
    Reference documentation: https://www.w3.org/TR/SVG11/coords.html

    Inputs:
        v_b:         Contents of SVG viewbox attribute
        p_a_r:      Contents of SVG preserveAspectRatio attribute
        doc_width:  Width of SVG document
        doc_height: Height of SVG document

    Output: s_x, s_y, o_x, o_y
        Scale parameters (s_x,s_y) and offset parameters (o_x,o_y)

    """
    if v_b is None:
        return 1, 1, 0, 0 # No viewbox; return default transform
    vb_array = v_b.strip().replace(',', ' ').split()

    if len(vb_array) < 4:
        return 1, 1, 0, 0 # invalid viewbox; return default transform

    min_x = float(vb_array[0]) # viewbox offset: x
    min_y = float(vb_array[1]) # viewbox offset: y
    width = float(vb_array[2]) # viewbox width
    height = float(vb_array[3]) # viewbox height

    if width <= 0 or height <= 0:
        return 1, 1, 0, 0 # invalid viewbox; return default transform

    d_width = float(doc_width)
    d_height = float(doc_height)

    if d_width <= 0 or d_height <= 0:
        return 1, 1, 0, 0 # invalid document size; return default transform

    ar_doc = d_height / d_width # Document aspect ratio
    ar_vb = height / width      # viewbox aspect ratio

    # Default values of the two preserveAspectRatio parameters:
    par_align = "xmidymid" # "align" parameter (lowercased)
    par_mos = "meet"       # "meetOrSlice" parameter

    if p_a_r is not None:
        par_array = p_a_r.strip().replace(',', ' ').lower().split()
        if len(par_array) > 0:
            par0 = par_array[0]
            if par0 == "defer":
                if len(par_array) > 1:
                    par_align = par_array[1]
                    if len(par_array) > 2:
                        par_mos = par_array[2]
            else:
                par_align = par0
                if len(par_array) > 1:
                    par_mos = par_array[1]

    if par_align == "none":
        # Scale document to fill page. Do not preserve aspect ratio.
        # This is not default behavior, nor what happens if par_align
        # is not given; the "none" value must be _explicitly_ specified.

        s_x = d_width/ width
        s_y = d_height / height
        o_x = -min_x
        o_y = -min_y
        return s_x, s_y, o_x, o_y

    # Other than "none", all situations fall into two classes:
    #
    # 1)   (ar_doc >= ar_vb AND par_mos == "meet")
    #        or  (ar_doc < ar_vb AND par_mos == "slice")
    #     -> In these cases, scale document up until viewbox fills doc in X.
    #
    # 2)   All other cases, i.e.,
    #     (ar_doc < ar_vb AND par_mos == "meet")
    #        or  (ar_doc >= ar_vb AND par_mos == "slice")
    #     -> In these cases, scale document up until viewbox fills doc in Y.
    #
    # Note in cases where the scaled viewbox exceeds the document
    # (page) boundaries (all "slice" cases and many "meet" cases where
    # an offset value is given) that this routine does not perform
    # any clipping, but subsequent clipping to the page boundary
    # is appropriate.
    #
    # Besides "none", there are 9 possible values of par_align:
    #     xminymin xmidymin xmaxymin
    #     xminymid xmidymid xmaxymid
    #     xminymax xmidymax xmaxymax

    if (((ar_doc >= ar_vb) and (par_mos == "meet"))
            or ((ar_doc < ar_vb) and (par_mos == "slice"))):
        # Case 1: Scale document up until viewbox fills doc in X.

        s_x = d_width / width
        s_y = s_x # Uniform aspect ratio
        o_x = -min_x

        scaled_vb_height = ar_doc * width
        excess_height = scaled_vb_height - height

        if par_align in {"xminymin", "xmidymin", "xmaxymin"}:
            # Case: Y-Min: Align viewbox to minimum Y of the viewport.
            o_y = -min_y

        elif par_align in {"xminymax", "xmidymax", "xmaxymax"}:
            # Case: Y-Max: Align viewbox to maximum Y of the viewport.
            o_y = -min_y + excess_height

        else: # par_align in {"xminymid", "xmidymid", "xmaxymid"}:
            # Default case: Y-Mid: Center viewbox on page in Y
            o_y = -min_y + excess_height / 2

        return s_x, s_y, o_x, o_y

    # Case 2: Scale document up until viewbox fills doc in Y.

    s_y = d_height / height
    s_x = s_y # Uniform aspect ratio
    o_y = -min_y

    scaled_vb_width = height / ar_doc
    excess_width = scaled_vb_width - width

    if par_align in {"xminymin", "xminymid", "xminymax"}:
        # Case: X-Min: Align viewbox to minimum X of the viewport.
        o_x = -min_x

    elif par_align in {"xmaxymin", "xmaxymid", "xmaxymax"}:
        # Case: X-Max: Align viewbox to maximum X of the viewport.
        o_x = -min_x + excess_width

    else: # par_align in {"xmidymin", "xmidymid", "xmidymax"}:
        # Default case: X-Mid: Center viewbox on page in X
        o_x = -min_x + excess_width / 2

    return s_x, s_y, o_x, o_y
    # return 1, 1, 0, 0 # Catch-all: return default transform


def points_equal(point_a, point_b):
    """
    Given two vertices point_a and point_b, each a 2-tuple,
    determine if the two points are close enough to be considered "equal"
    with a floating-point-friendly "fuzzy" comparison.
    """
    return isclose(point_a[0], point_b[0]) and isclose(point_a[1], point_b[1])


def points_near(point_a, point_b, squared_tolerance):
    """
    Given two vertices point_a and point_b, each a 2-tuple, return True if the two
    points are coincident to within a certain tolerance.

    Arguments:
        point_a, point_b:  Vertex (x,y), 2-tuples of floats
        squared_tolerance: Square of maximum allowed distance between vertices

    if (point_a.x - point_b.x)^2 + (point_a.y - point_b.y)^2 < tolerance^2,
        then return True.
    """
    delta_x = point_a[0] - point_b[0]
    delta_y = point_a[1] - point_b[1]

    return (delta_x * delta_x + delta_y * delta_y) < squared_tolerance


def square_dist(point_a, point_b):
    """
    Given two vertices point_a and point_b, each a 2-tuple,
    return the square of the distance between them.
    """
    delta_x = point_a[0] - point_b[0]
    delta_y = point_a[1] - point_b[1]
    return delta_x * delta_x + delta_y * delta_y


def points_near(point_a, point_b, squared_tolerance):
    """
    Given two vertices point_a and point_b, each a 2-tuple, return True if the two
    points are coincident to within a certain tolerance.

    Arguments:
        point_a, point_b:  Vertex (x,y), 2-tuples of floats
        squared_tolerance: Square of maximum allowed distance between vertices

    if (point_a.x - point_b.x)^2 + (point_a.y - point_b.y)^2 < tolerance^2,
        then return True.
    """
    delta_x = point_a[0] - point_b[0]
    delta_y = point_a[1] - point_b[1]

    return (delta_x * delta_x + delta_y * delta_y) < squared_tolerance


def square_dist(point_a, point_b):
    """
    Given two vertices point_a and point_b, each a 2-tuple,
    return the square of the distance between them.
    """
    delta_x = point_a[0] - point_b[0]
    delta_y = point_a[1] - point_b[1]
    return delta_x * delta_x + delta_y * delta_y


def vInitial_VF_A_Dx(v_final, acceleration, delta_x):
    """
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
    """
    initial_v_squared = (v_final * v_final) - (2 * acceleration * delta_x)
    if initial_v_squared >= 0:
        return sqrt(initial_v_squared)
    return -1


def vFinal_Vi_A_Dx(v_initial, acceleration, delta_x):
    """
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
    """
    final_v_squared = (2 * acceleration * delta_x) + (v_initial * v_initial)
    if final_v_squared >= 0:
        return sqrt(final_v_squared)
    return -1


def pathdata_first_point(path):
    """
    Return the first (X,Y) point from an SVG path data string

    Input:  A path data string; the text of the 'd' attribute of an SVG path
    Output: Two floats in a list representing the x and y coordinates of the first point
    """

    parsed_path = simplepath.parsePath(path) # parsePath splits path into segments

    for command, params in parsed_path:
        if command == 'M':
            return [params[0], params[1]]

    # Properly constructed paths begin with a moveto ('M') command.
    return None


def pathdata_last_point(path):
    """
    Return the last (X,Y) point from an SVG path data string

    Input:  A path data string; the text of the 'd' attribute of an SVG path
    Output: Two floats in a list representing the x and y coordinates of the last point
    """
    parsed_path = simplepath.parsePath(path) # parsePath splits path into segments
    command, params = parsed_path[-1] # look at the last command to determine the last point

    if command.upper() == 'Z':
        # find the last move command, since Z moves to the start of the last subpath
        for command, params in reversed(parsed_path[:-1]):
            if command == 'M':
                return [params[0], params[1]]

        # paths must have at least one moveto, so we should never get here.
        return None

    # Otherwise: The last command should be in the set 'MLCQA'
    #     - All commands converted to absolute by parsePath.
    #     - Can ignore Z (case handled)
    #     - Can ignore H,V, since those are converted to L by parsePath.
    #     - Can ignore S, converted to C by parsePath.
    #     - Can ignore T, converted to Q by parsePath.
    #
    #     MLCQA: Commands all ending in (X,Y) pair.

    x_val = params[-2] # Second to last parameter given
    y_val = params[-1] # Last parameter given

    return [x_val, y_val]
