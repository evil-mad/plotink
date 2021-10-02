"""
Tests for plot_utils.py

part of https://github.com/evil-mad/plotink

"""

import unittest
import copy
import random
import math

from plotink import plot_utils
from plotink import ebb_motion

from plotink.plot_utils_import import from_dependency_import

cspsubdiv = from_dependency_import('ink_extensions.cspsubdiv')

# python -m unittest discover in top-level package dir

# pylint: disable=too-many-public-methods



class PlotUtilsTestCase(unittest.TestCase):
    """
    Unit tests for plot_utils.py
    """

    def test_px_per_inch(self):
        """ test PX_PER_INCH constant """
        self.assertEqual(96, plot_utils.PX_PER_INCH)

    def test_check_limits(self):
        """ test checkLimits function """
        low_lim = -23.5
        hi_lim = 47.1234
        value_input = 25
        constrained, out_of_bounds = plot_utils.checkLimits(value_input, low_lim, hi_lim)
        self.assertEqual(constrained, value_input)
        self.assertFalse(out_of_bounds)
        value_input = -100
        constrained, out_of_bounds = plot_utils.checkLimits(value_input, low_lim, hi_lim)
        self.assertEqual(constrained, low_lim)
        self.assertTrue(out_of_bounds)
        value_input = 100
        constrained, out_of_bounds = plot_utils.checkLimits(value_input, low_lim, hi_lim)
        self.assertEqual(constrained, hi_lim)
        self.assertTrue(out_of_bounds)

    def test_check_limits_tol(self):
        """ test checkLimitsTol function """
        low_lim = -23.5
        hi_lim = 47.1234
        tol = 0.01
        value_input = 25
        constrained, out_of_bounds = plot_utils.checkLimitsTol(value_input, low_lim, hi_lim, tol)
        self.assertEqual(constrained, value_input)
        self.assertFalse(out_of_bounds)
        value_input = -100
        constrained, out_of_bounds = plot_utils.checkLimitsTol(value_input, low_lim, hi_lim, tol)
        self.assertEqual(constrained, low_lim)
        self.assertTrue(out_of_bounds)
        value_input = 100
        constrained, out_of_bounds = plot_utils.checkLimitsTol(value_input, low_lim, hi_lim, tol)
        self.assertEqual(constrained, hi_lim)
        self.assertTrue(out_of_bounds)
        low_lim = 10.0
        hi_lim = 90.0
        value_input = 9.999
        constrained, out_of_bounds = plot_utils.checkLimitsTol(value_input, low_lim, hi_lim, tol)
        self.assertEqual(constrained, low_lim)
        self.assertFalse(out_of_bounds)
        value_input = 90.009
        constrained, out_of_bounds = plot_utils.checkLimitsTol(value_input, low_lim, hi_lim, tol)
        self.assertEqual(constrained, hi_lim)
        self.assertFalse(out_of_bounds)

    def test_constrain_limits(self):
        """ test constrainLimits function """
        low_lim = -23.5
        hi_lim = 47.1234
        value_input = 25
        constrained = plot_utils.constrainLimits(value_input, low_lim, hi_lim)
        self.assertEqual(constrained, value_input)
        value_input = -100
        constrained = plot_utils.constrainLimits(value_input, low_lim, hi_lim)
        self.assertEqual(constrained, low_lim)
        value_input = 100
        constrained = plot_utils.constrainLimits(value_input, low_lim, hi_lim)
        self.assertEqual(constrained, hi_lim)

    def test_distance(self):
        """ test distance function """
        self.assertEqual(1, plot_utils.distance(1, 0))
        self.assertEqual(1, plot_utils.distance(0, -1))
        self.assertEqual(2 * math.sqrt(2), plot_utils.distance(-2, -2))

    def test_dot_product_xy(self):
        """ test dotProductXY function """
        vector_a = (1, 0)
        vector_b = (0, 1)
        self.assertEqual(0, plot_utils.dotProductXY(vector_a, vector_b))
        self.assertEqual(1, plot_utils.dotProductXY(vector_a, vector_a))
        vector_a = (1, 1)
        self.assertEqual(1, plot_utils.dotProductXY(vector_a, vector_a))
        vector_b = (-1, -1)
        self.assertEqual(-1, plot_utils.dotProductXY(vector_a, vector_b))
        vector_a = (0.5, 0.5)
        vector_b = (0, 0.5)
        self.assertEqual(0.25, plot_utils.dotProductXY(vector_a, vector_b))

    def test_parse_length_units(self):
        """ test parseLengthWithUnits function """
        unit_string = "50px"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(50, the_value)
        self.assertEqual("px", the_units)

        unit_string = "-128.129151in"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(-128.129151, the_value)
        self.assertEqual("in", the_units)

        unit_string = "0.200001mm"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(0.200001, the_value)
        self.assertEqual("mm", the_units)

        unit_string = "-0.200001cm"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(-0.200001, the_value)
        self.assertEqual("cm", the_units)

        unit_string = "30E7pt"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(30E7, the_value)
        self.assertEqual("pt", the_units)

        unit_string = "-0.30E3pc"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(-0.30E3, the_value)
        self.assertEqual("pc", the_units)

        unit_string = "128Q"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(128, the_value)
        self.assertEqual("Q", the_units)

        unit_string = "128q"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(128, the_value)
        self.assertEqual("Q", the_units)

        unit_string = "-25.01%"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(-25.01, the_value)
        self.assertEqual("%", the_units)

        unit_string = "50r6cm"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(None, the_value)
        self.assertEqual(None, the_units)

        unit_string = "56zm"
        the_value, the_units = plot_utils.parseLengthWithUnits(unit_string)
        self.assertEqual(None, the_value)
        self.assertEqual(None, the_units)

    def test_position_scale(self):
        """ test position_scale function """
        for i in range(5):
            [x_in, y_in] =  [random.random(), random.random()]
            x_out, y_out = plot_utils.position_scale(x_in, y_in, None)
            self.assertEqual(x_out, x_in)
            self.assertEqual(y_out, y_in)
            x_out, y_out = plot_utils.position_scale(x_in, y_in, 1)
            self.assertEqual(x_out, x_in * 2.54)
            self.assertEqual(y_out, y_in * 2.54)
            x_out, y_out = plot_utils.position_scale(x_in, y_in, 2)
            self.assertEqual(x_out, x_in * 25.4)
            self.assertEqual(y_out, y_in * 25.4)

    def test_subdiv_no_divisions(self):
        """ Tests for subdivideCubicPath
        when applied to a straight line, there will be no subdivisions as the "curve"
        can be represented easily as only one/two segments """
        orig_beziers = [[(0, 0), (0.5, 0.5), (1, 1)],
                        [(1.25, 1.25), (1.75, 1.75), (2, 2)]]
        processed_beziers = copy.deepcopy(orig_beziers)

        plot_utils.subdivideCubicPath(processed_beziers, 0)

        self.assertEqual(orig_beziers, processed_beziers)

    def test_subdiv_divisions(self):
        """ Tests for subdivideCubicPath with divisions """
        orig_beziers = [[(1, 1), (2, 2), (0, 0)],
                        [(2, 2), (1, 1), (0, 0)]]
        processed_beziers = copy.deepcopy(orig_beziers)

        plot_utils.subdivideCubicPath(processed_beziers, .2)

        self.assertGreater(len(processed_beziers), len(orig_beziers))
        # but some things should not be modified
        self.assertEqual(orig_beziers[1][1:], processed_beziers[len(processed_beziers) - 1][1:])

    def test_max_dist_from_n_points_1(self):
        """ behavior for one point """
        input_points = [(0, 0), (5, 5), (10, 0)]

        self.assertEqual(5, plot_utils.max_dist_from_n_points(input_points))

    def test_max_dist_from_n_points_2(self):
        """ check that the results are the same as the original maxdist """
        inputs = [self.get_random_points(4, i + .01) for i in range(5)]  # check a few possibilities

        for in_item in inputs:
            self.assertEqual(cspsubdiv.maxdist(in_item), plot_utils.max_dist_from_n_points(in_item))

    def test_max_dist_from_n_points_3(self):
        """ behavior for three points """
        input_points = [(0, 0), (0, 3), (-4, 0), (4, -7), (10, 0)]

        self.assertEqual(7, plot_utils.max_dist_from_n_points(input_points))

    def test_points_equal(self):
        """ Test floating-point-friendly fuzzy vertex point comparison """
        point_a = (5, 6)
        point_b = (point_a[0] + 1E-10, point_a[1] - 1E-10)
        point_c = (point_a[0] + 1E-4, point_a[1] - 1E-4)
        self.assertTrue(plot_utils.points_equal(point_a, point_b))
        self.assertFalse(plot_utils.points_equal(point_a, point_c))

    def test_points_near(self):
        """ Test floating-point-friendly fuzzy vertex point comparison """
        point_a = (5, 6)
        point_b = (point_a[0] + 1E-3, point_a[1] - 1E-3)
        sq_tol = 0.002 ** 2
        self.assertTrue(plot_utils.points_near(point_a, point_b, sq_tol))
        sq_tol = .0005 ** 2
        self.assertFalse(plot_utils.points_near(point_a, point_b, sq_tol))

    def test_points_near(self):
        """ Test analysis of point inside bounds """
        point_a = (-1, 6)
        point_b = (5, -6)
        point_c = (-5, -6)
        point_d = (5, 6)
        point_e = (-1E-11, 6)
        point_f = (3, 10 + 1E-8)
        bounds_a = [[0, 0], [10, 10]]
        self.assertFalse(plot_utils.point_in_bounds(point_a, bounds_a))
        self.assertFalse(plot_utils.point_in_bounds(point_b, bounds_a))
        self.assertFalse(plot_utils.point_in_bounds(point_c, bounds_a))
        self.assertTrue(plot_utils.point_in_bounds(point_d, bounds_a))
        self.assertTrue(plot_utils.point_in_bounds(point_e, bounds_a))
        self.assertTrue(plot_utils.point_in_bounds(point_e, bounds_a,1e-9))
        self.assertFalse(plot_utils.point_in_bounds(point_e, bounds_a,1e-13))
        self.assertFalse(plot_utils.point_in_bounds(point_e, bounds_a,0))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a,0))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a,1e-12))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a,0))
        self.assertTrue(plot_utils.point_in_bounds(point_f, bounds_a,0.001))

    def test_square_dist(self):
        """ Test floating-point-friendly fuzzy vertex point comparison """
        point_a = (0, 0)
        point_b = (-3, 4)
        self.assertEqual(25, plot_utils.square_dist(point_a, point_b))

    def test_supersample_few_vertices(self):
        """ supersample returns the list of vertices unchanged if the list is too small (<= 2) """
        vertices = [self.get_random_points(i, i) for i in range(3)] # inputs of size 1, 2, 3

        for orig_vertices in vertices:
            processed_vertices = copy.deepcopy(orig_vertices)
            plot_utils.supersample(processed_vertices, 0)
            self.assertEqual(orig_vertices, processed_vertices)

    def test_supersample_no_deletions(self):
        """ Test case for supersampling """
        orig_vertices = self.get_random_points(12, 1)
        tolerance = -1 # an impossibly low tolerance

        processed_vertices = copy.deepcopy(orig_vertices)
        plot_utils.supersample(processed_vertices, tolerance)
        self.assertEqual(orig_vertices, processed_vertices)

    def test_supersample_delete_one(self):
        """ Test case for supersampling """
        tolerance = 1
        vertices = [[(0, 0), (0, tolerance - .1), (2, 0)],
                    [(0, 0), (1, tolerance - .2), (2, 0), (3, tolerance + 20000), (4, 0)]]

        for orig_vertices in vertices:
            processed_vertices = copy.deepcopy(orig_vertices)
            plot_utils.supersample(processed_vertices, tolerance)

            self.assertEqual(len(orig_vertices) - 1, len(processed_vertices), # removed one exactly
                             "Incorrect result: {}".format(processed_vertices))
            # other vertices stayed the same
            self.assertEqual(orig_vertices[0], processed_vertices[0])
            for i in range(2, len(orig_vertices)):
                self.assertEqual(orig_vertices[i], processed_vertices[i - 1])

    def test_supersample_delete_groups(self):
        """ Test case for supersampling """
        tolerance = .05
        vertices = [(0, 10), (tolerance - .02, 9), (0, 8), # del 1
                    (1, 8), (2, 8 + tolerance / 2), (3, 8 + tolerance / 3), (4, 8), # del 3
                    (4, 7), (5, 7), (5, 6), # no deletions
                    (0, 0), (1, tolerance - .01), (2, 0)] # del 1 again

        expected_result = [(0, 10), (0, 8),
                           (4, 8),
                           (4, 7), (5, 7), (5, 6),
                           (0, 0), (2, 0)]

        plot_utils.supersample(vertices, tolerance)

        self.assertEqual(expected_result, vertices)

    def test_supersample_delete_all(self):
        """ Test case for supersampling """
        vertices = [self.get_random_points(i + 3, i + 1) for i in range(5)]
        tolerance = 100 # guaranteed to be higher than any of the distances

        for orig_vertices in vertices:
            processed_vertices = copy.deepcopy(orig_vertices)
            plot_utils.supersample(processed_vertices, tolerance)

            self.assertEqual(2, len(processed_vertices), # deleted all but start and end
                             "Error for test case {}. Should be length 2, instead got {}"
                             .format(orig_vertices, processed_vertices))
            # start and end are the same
            self.assertEqual(orig_vertices[0], processed_vertices[0])
            self.assertEqual(orig_vertices[len(orig_vertices) - 1], processed_vertices[1])

    def test_pathdata_first_point(self):
        """ Test pathdata_first_point function """
        path_d = """
        M 0.6823228,0.74095991 c 0.709525,0.89502916 0.6320138,1.0767057 0.7143067,1.2207181
        c 0.0298568,0.052249 0.15408663,0.058637 0.20789523,0.058637
        """

        x_out, y_out = plot_utils.pathdata_first_point(path_d)
        self.assertEqual(x_out, 0.6823228)
        self.assertEqual(y_out, 0.74095991)

    def test_pathdata_last_point(self):
        """ Test pathdata_last_point function """
        path_d = """
        M 0.6823228,0.74095991 c 0.709525,0.89502916 0.6320138,1.0767057 0.7143067,1.2207181
        c 0.0298568,0.052249 0.15408663,0.058637 0.20789523,0.058637
        """
        x_out, y_out = plot_utils.pathdata_last_point(path_d)
        self.assertEqual(x_out, 1.60452473)
        self.assertEqual(y_out, 2.02031501)
        path_d = path_d.upper()
        x_out, y_out = plot_utils.pathdata_last_point(path_d)
        self.assertEqual(x_out, 0.20789523)
        self.assertEqual(y_out, 0.058637)
        path_e = path_d + 'z'
        x_out, y_out = plot_utils.pathdata_last_point(path_e)
        self.assertEqual(x_out, 0.6823228)
        self.assertEqual(y_out, 0.74095991)
        path_f = path_e + """ M 0.88488738,1.0288149 1.0714601,0.76761311 C 0.062066,0.016927
        0.1066128,0.31557069 0.1066128,0.34649199"""
        x_out, y_out = plot_utils.pathdata_last_point(path_f)
        self.assertEqual(x_out, 0.1066128)
        self.assertEqual(y_out, 0.34649199)
        path_g = path_f + 'z'
        x_out, y_out = plot_utils.pathdata_last_point(path_g)
        self.assertEqual(x_out, 0.88488738)
        self.assertEqual(y_out, 1.0288149)

    def test_moveTimeLM(self):
        """ Test moveTimeLM function """
        move_time = ebb_motion.moveTimeLM(412361511,1119,-35357)
        self.assertEqual(move_time, 11362)
        move_time = ebb_motion.moveTimeLM(47141172,4478,141428)
        self.assertEqual(move_time, 11333)

    def test_moveDistLM(self):
        """ Test moveDistLM function """
        move_dist = ebb_motion.moveDistLM(412361511, -35357, 11362) # 1119
        self.assertEqual(move_dist, 1119)
        move_dist = ebb_motion.moveDistLM(47141172, 141428, 11333) #4478 
        self.assertEqual(move_dist, 4478)

    @staticmethod
    def get_random_points(num, seed=0):
        """ generate random (but deterministic) points where coords are between 0 and 1 """
        random.seed(seed)

        return [(random.random(), random.random()) for _ in range(num)]
