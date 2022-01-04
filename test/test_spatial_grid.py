"""
Tests for spatial_grid.py

part of https://github.com/evil-mad/plotink

"""

import unittest

from plotink import spatial_grid

# python -m unittest discover in top-level package dir

# pylint: disable=too-many-public-methods


class SpatialGridTestCase(unittest.TestCase):
    """
    Tests for spatial_grid.py
    """

    def test_format_hms(self):
        """
        Unit tests for spatial_grid.py
        """
        endpoints = [
                    [[61.32, 26.04], [7.62, 6.74]],
                    [[6.66, 12.31], [59.84, 13.43]],
                    [[54.43, 2.27], [72.02, 50.23]],
                    [[23.91, 6.7], [29.29, 25.73]],
                    [[71.93, 84.14], [68.63, 11.17]],
                    [[45.16, 42.48], [90.03, 49.43]],
                    [[70.2, 69.32], [38.34, 16.14]],
                    [[87.29, 83.05], [4.41, 57.89]],
                    [[92.37, 61.91], [86.33, 64.66]],
                    [[80.05, 28.2], [33.17, 70.01]],
                    [[71.96, 12.39], [67.58, 88.27]],
                    [[7.77, 94.55], [3.01, 25.53]],
                    [[71.69, 76.16], [50.15, 80.09]],
                    [[9.56, 27.56], [0.28, 62.84]],
                    [[45.82, 72.35], [84.99, 20.82]],
                    [[19.31, 8.15], [5.35, 49.68]],
                    [[84.48, 12.28], [34.67, 35.75]],
                    [[92.57, 75.07], [15.77, 21.47]],
                    [[49.8, 56.31], [56.28, 84.44]],
                    [[73.35, 3.25], [23.33, 0.32]],
                    [[77.35, 12.98], [14.81, 3.15]],
                    [[13.3, 0.11], [76.49, 21.11]],
                    [[85.75, 17.98], [90.68, 73.08]],
                    [[64.04, 90.32], [91.85, 71.93]],
                    [[38.12, 73.22], [34.37, 2.51]],
                    [[38.82, 10.99], [54.79, 70.56]],
                    [[18.99, 3.85], [17.38, 0.7]],
                    [[42.15, 7.26], [51.24, 14.13]]
                    ]
        grid_index = spatial_grid.Index(endpoints, 4, True)

        # test spatial_grid function init
        self.assertEqual(sorted(grid_index.adjacents[8]), sorted([4, 5, 8, 9, 12, 13]))
        self.assertEqual(grid_index.path_count, 28)
        self.assertEqual(grid_index.vertices, endpoints)
        self.assertEqual(grid_index.reverse, True)
        self.assertEqual(grid_index.xmin < 0, True)


        self.assertEqual(grid_index.bins_per_side, 4)
        self.assertEqual(len(grid_index.grid), 16)
        self.assertEqual(len(grid_index.lookup), 56)
        self.assertEqual(grid_index.nearest([0, 0]), 28) # End of first path is closest to 0, 0
        self.assertEqual(grid_index.lookup[28], 0) # Path end is in grid cell 0
        # Contents of grid cell 0:
        self.assertEqual(sorted(grid_index.grid[0]), sorted([1, 15, 21, 26, 28, 45, 48, 54]))

        grid_index.remove_path(0) # Should remove path number 28 as well.
        self.assertEqual(sorted(grid_index.grid[0]), sorted([1, 15, 21, 26, 45, 48, 54]))

        # Find nearest remaining vertex to [0,0]:
        self.assertEqual(grid_index.nearest([0, 0]), 21)
