'''
rtree.py

Minimal R-tree spatial index class for calculating intersecting regions

Written by Michal Migurski https://github.com/migurski @michalmigurski
as a contribution to the AxiDraw project https://github.com/evil-mad/axidraw/


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

__version__ = "1.1" # Dated 2024-05-13

import math

def version():    # Version number for this document
    """Return version number of this script"""
    return __version__

class Index:
    ''' One-shot R-Tree index (no rebalancing, insertions, etc.)
    '''
    bboxes = []
    subtrees = []
    xmin = None
    ymin = None
    xmax = None
    ymax = None

    def __init__(self, bboxes):
        center_x, center_y = 0, 0
        self.xmin, self.ymin = math.inf, math.inf
        self.xmax, self.ymax = -math.inf, -math.inf

        for (_, (xmin, ymin, xmax, ymax)) in bboxes:
            center_x += (xmin/2 + xmax/2) / len(bboxes)
            center_y += (ymin/2 + ymax/2) / len(bboxes)
            self.xmin = min(self.xmin, xmin)
            self.ymin = min(self.ymin, ymin)
            self.xmax = max(self.xmax, xmax)
            self.ymax = max(self.ymax, ymax)

        # Make four lists of bboxes, one for each quadrant around the center point
        # An original bbox may be present in more than one list
        sub_bboxes = [
            [
                (i, (x_1, y_1, x_2, y_2)) for (i, (x_1, y_1, x_2, y_2)) in bboxes
                if x_1 < center_x and y_1 < center_y
            ],
            [
                (i, (x_1, y_1, x_2, y_2)) for (i, (x_1, y_1, x_2, y_2)) in bboxes
                if x_2 > center_x and y_1 < center_y
            ],
            [
                (i, (x_1, y_1, x_2, y_2)) for (i, (x_1, y_1, x_2, y_2)) in bboxes
                if x_1 < center_x and y_2 > center_y
            ],
            [
                (i, (x_1, y_1, x_2, y_2)) for (i, (x_1, y_1, x_2, y_2)) in bboxes
                if x_2 > center_x and y_2 > center_y
            ],
        ]

        # Store bboxes or subtrees but not both
        if max(map(len, sub_bboxes)) == len(bboxes):
            # One of the subtrees is identical to the whole tree so just keep all the bboxes
            self.bboxes = bboxes
        else:
            # Make four subtrees, one for each quadrant
            self.subtrees = [Index(sub) for sub in sub_bboxes]

    def intersection(self, bbox):
        ''' Get a set of IDs for a given bounding box
        '''
        ids, (x_1, y_1, x_2, y_2) = set(), bbox

        for (i, (xmin, ymin, xmax, ymax)) in self.bboxes:
            is_disjoint = x_1 > xmax or y_1 > ymax or x_2 < xmin or y_2 < ymin
            if not is_disjoint:
                ids.add(i)

        for subt in self.subtrees:
            is_disjoint = x_1 > subt.xmax or y_1 > subt.ymax or x_2 < subt.xmin or y_2 < subt.ymin
            if not is_disjoint:
                ids |= subt.intersection(bbox)

        return ids
