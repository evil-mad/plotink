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
            [x_in, y_in] = [random.random(), random.random()]
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

        plot_utils.subdivideCubicPath(processed_beziers, .01)

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

    def test_point_in_bounds(self):
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
        self.assertTrue(plot_utils.point_in_bounds(point_e, bounds_a, 1e-9))
        self.assertFalse(plot_utils.point_in_bounds(point_e, bounds_a, 1e-13))
        self.assertFalse(plot_utils.point_in_bounds(point_e, bounds_a, 0))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a, 0))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a, 1e-12))
        self.assertFalse(plot_utils.point_in_bounds(point_f, bounds_a, 0))
        self.assertTrue(plot_utils.point_in_bounds(point_f, bounds_a, 0.001))

    def test_square_dist(self):
        """ Test floating-point-friendly fuzzy vertex point comparison """
        point_a = (0, 0)
        point_b = (-3, 4)
        self.assertEqual(25, plot_utils.square_dist(point_a, point_b))

    def test_supersample_few_vertices(self):
        """ supersample returns the list of vertices unchanged if the list is too small (<= 2) """
        vertices = [self.get_random_points(i, i) for i in range(3)]  # inputs of size 1, 2, 3

        for orig_vertices in vertices:
            processed_vertices = copy.deepcopy(orig_vertices)
            plot_utils.supersample(processed_vertices, 0)
            self.assertEqual(orig_vertices, processed_vertices)

    def test_supersample_no_deletions(self):
        """ Test case for supersampling """
        orig_vertices = self.get_random_points(12, 1)
        tolerance = -1  # an impossibly low tolerance

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

            self.assertEqual(len(orig_vertices) - 1, len(processed_vertices),  # removed one exactly
                             "Incorrect result: {}".format(processed_vertices))
            # other vertices stayed the same
            self.assertEqual(orig_vertices[0], processed_vertices[0])
            for i in range(2, len(orig_vertices)):
                self.assertEqual(orig_vertices[i], processed_vertices[i - 1])

    def test_supersample_delete_groups(self):
        """ Test case for supersampling """
        tolerance = .05
        vertices = [(0, 10), (tolerance - .02, 9), (0, 8),  # del 1
                    (1, 8), (2, 8 + tolerance / 2), (3, 8 + tolerance / 3), (4, 8),  # del 3
                    (4, 7), (5, 7), (5, 6),  # no deletions
                    (0, 0), (1, tolerance - .01), (2, 0)]  # del 1 again

        expected_result = [(0, 10), (0, 8),
                           (4, 8),
                           (4, 7), (5, 7), (5, 6),
                           (0, 0), (2, 0)]

        plot_utils.supersample(vertices, tolerance)

        self.assertEqual(expected_result, vertices)

    def test_supersample_delete_all(self):
        """ Test case for supersampling """
        vertices = [self.get_random_points(i + 3, i + 1) for i in range(5)]
        tolerance = 100  # guaranteed to be higher than any of the distances

        for orig_vertices in vertices:
            processed_vertices = copy.deepcopy(orig_vertices)
            plot_utils.supersample(processed_vertices, tolerance)

            self.assertEqual(2, len(processed_vertices),  # deleted all but start and end
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
        move_time = ebb_motion.moveTimeLM(412361511, 1119, -35357)
        self.assertEqual(move_time, 11362)
        move_time = ebb_motion.moveTimeLM(47141172, 4478, 141428)
        self.assertEqual(move_time, 11333)

    def test_moveDistLM(self):
        """ Test moveDistLM function """
        move_dist = ebb_motion.moveDistLM(412361511, -35357, 11362)  # 1119
        self.assertEqual(move_dist, 1119)
        move_dist = ebb_motion.moveDistLM(47141172, 141428, 11333)  # 4478
        self.assertEqual(move_dist, 4478)

    def test_vb_scale_no_viewbox(self):
        """ Test vb_scale with None viewbox """
        result = plot_utils.vb_scale(None, None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

    def test_vb_scale_invalid_viewbox_format(self):
        """ Test vb_scale with invalid viewbox formats """
        # Less than 4 values
        result = plot_utils.vb_scale("0 0 100", None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

        # Non-numeric values (should raise ValueError in current implementation)
        with self.assertRaises(ValueError):
            plot_utils.vb_scale("0 0 abc 100", None, 1.0, 1.0)

        # Empty string
        result = plot_utils.vb_scale("", None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

    def test_vb_scale_invalid_viewbox_dimensions(self):
        """ Test vb_scale with invalid viewbox dimensions """
        # Zero width
        result = plot_utils.vb_scale("0 0 0 100", None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

        # Zero height
        result = plot_utils.vb_scale("0 0 100 0", None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

        # Negative width
        result = plot_utils.vb_scale("0 0 -100 100", None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

        # Negative height
        result = plot_utils.vb_scale("0 0 100 -100", None, 1.0, 1.0)
        self.assertEqual(result, (1, 1, 0, 0))

    def test_vb_scale_invalid_document_dimensions(self):
        """ Test vb_scale with invalid document dimensions """
        # Zero document width
        result = plot_utils.vb_scale("0 0 100 100", None, 0, 1)
        self.assertEqual(result, (1, 1, 0, 0))

        # Zero document height
        result = plot_utils.vb_scale("0 0 100 100", None, 1, 0)
        self.assertEqual(result, (1, 1, 0, 0))

        # Negative document width
        result = plot_utils.vb_scale("0 0 100 100", None, -1, 1)
        self.assertEqual(result, (1, 1, 0, 0))

        # Negative document height
        result = plot_utils.vb_scale("0 0 100 100", None, 1, -1)
        self.assertEqual(result, (1, 1, 0, 0))

    def test_vb_scale_identity_transform(self):
        """ Test vb_scale with viewbox that should produce identity transform """
        # 1:1 mapping in inches - like debug_0b.svg
        result = plot_utils.vb_scale("0 0 11 8.5", None, 11.0, 8.5)
        s_x, s_y, o_x, o_y = result
        # Should be close to (1, 1, 0, 0) but may not be exactly due to unit conversion
        self.assertAlmostEqual(s_x, 1.0, places=5)
        self.assertAlmostEqual(s_y, 1.0, places=5)
        self.assertAlmostEqual(o_x, 0.0, places=5)
        self.assertAlmostEqual(o_y, 0.0, places=5)

    def test_vb_scale_scaling_required(self):
        """ Test vb_scale with viewbox requiring scaling - like debug_2b.svg """
        # viewBox="0 0 279.4 215.9" with width="11in" height="8.5in"
        result = plot_utils.vb_scale("0 0 279.4 215.9", None, 11.0, 8.5)
        s_x, s_y, o_x, o_y = result
        # Should have scaling factors but not (1,1,0,0)
        self.assertNotEqual(result, (1, 1, 0, 0))
        self.assertGreater(s_x, 0)
        self.assertGreater(s_y, 0)

    def test_vb_scale_with_offset(self):
        """ Test vb_scale with viewbox that has non-zero offset """
        # Convert 100px to inches: 100px / 96 px/inch = ~1.04 inches
        doc_size_inches = 100.0 / 96.0
        result = plot_utils.vb_scale("10 20 100 100", None, doc_size_inches, doc_size_inches)
        s_x, s_y, o_x, o_y = result
        self.assertNotEqual(result, (1, 1, 0, 0))
        # Should have negative offsets to account for viewbox offset
        self.assertLess(o_x, 0)
        self.assertLess(o_y, 0)

    def test_vb_scale_comma_separated(self):
        """ Test vb_scale with comma-separated viewbox """
        # Convert 100px to inches: 100px / 96 px/inch = ~1.04 inches
        doc_size_inches = 100.0 / 96.0
        result = plot_utils.vb_scale("0,0,100,100", None, doc_size_inches, doc_size_inches)
        s_x, s_y, o_x, o_y = result
        self.assertNotEqual(result, (1, 1, 0, 0))
        self.assertGreater(s_x, 0)
        self.assertGreater(s_y, 0)

    def test_vb_scale_pixel_units(self):
        """ Test vb_scale with pixel-based units """
        # Test a case where viewBox matches document in pixels
        # 96px document = 1 inch, viewBox "0 0 96 96" should give scale close to 1/96
        result = plot_utils.vb_scale("0 0 96 96", None, 1.0, 1.0)
        s_x, s_y, o_x, o_y = result
        self.assertNotEqual(result, (1, 1, 0, 0))
        self.assertAlmostEqual(s_x, 1.0/96.0, places=5)
        self.assertAlmostEqual(s_y, 1.0/96.0, places=5)

    def test_vb_scale_2_none_for_invalid_viewbox(self):
        """ Test vb_scale_2 returns None for invalid viewBox cases """
        # No viewBox
        result = plot_utils.vb_scale_2(None, None, 1.0, 1.0)
        self.assertIsNone(result)

        # Less than 4 values
        result = plot_utils.vb_scale_2("0 0 100", None, 1.0, 1.0)
        self.assertIsNone(result)

        # Non-numeric values
        result = plot_utils.vb_scale_2("0 0 abc 100", None, 1.0, 1.0)
        self.assertIsNone(result)

        # Zero width
        result = plot_utils.vb_scale_2("0 0 0 100", None, 1.0, 1.0)
        self.assertIsNone(result)

        # Negative height
        result = plot_utils.vb_scale_2("0 0 100 -100", None, 1.0, 1.0)
        self.assertIsNone(result)

        # Zero document width
        result = plot_utils.vb_scale_2("0 0 100 100", None, 0, 1.0)
        self.assertIsNone(result)

    def test_vb_scale_2_valid_viewbox_cases(self):
        """ Test vb_scale_2 returns valid tuples for valid viewBox cases """
        # Identity transform case - should match vb_scale result
        result_original = plot_utils.vb_scale("0 0 11 8.5", None, 11.0, 8.5)
        result_new = plot_utils.vb_scale_2("0 0 11 8.5", None, 11.0, 8.5)
        self.assertIsNotNone(result_new)
        self.assertEqual(result_original, result_new)

        # Scaling required case - should match vb_scale result
        result_original = plot_utils.vb_scale("0 0 279.4 215.9", None, 11.0, 8.5)
        result_new = plot_utils.vb_scale_2("0 0 279.4 215.9", None, 11.0, 8.5)
        self.assertIsNotNone(result_new)
        self.assertEqual(result_original, result_new)

        # Offset case - should match vb_scale result
        doc_size_inches = 100.0 / 96.0
        result_original = plot_utils.vb_scale("10 20 100 100", None,
                                              doc_size_inches, doc_size_inches)
        result_new = plot_utils.vb_scale_2("10 20 100 100", None, doc_size_inches, doc_size_inches)
        self.assertIsNotNone(result_new)
        self.assertEqual(result_original, result_new)

    def test_vb_scale_2_preserve_aspect_ratio_none(self):
        """ Test vb_scale_2 with preserveAspectRatio='none' """
        # Test with "none" preserveAspectRatio - should not preserve aspect ratio
        result = plot_utils.vb_scale_2("0 0 100 200", "none", 2.0, 1.0)
        self.assertIsNotNone(result)
        s_x, s_y, o_x, o_y = result
        # Should not preserve aspect ratio - different scales for X and Y
        self.assertNotEqual(s_x, s_y)
        self.assertAlmostEqual(s_x, 2.0/100.0, places=6)  # doc_width/vb_width
        self.assertAlmostEqual(s_y, 1.0/200.0, places=6)  # doc_height/vb_height

    def test_vb_scale_2_preserve_aspect_ratio_default(self):
        """ Test vb_scale_2 with default preserveAspectRatio (should preserve aspect ratio) """
        result = plot_utils.vb_scale_2("0 0 100 200", None, 2.0, 1.0)
        self.assertIsNotNone(result)
        s_x, s_y, o_x, o_y = result
        # Should preserve aspect ratio - same scale for X and Y
        self.assertEqual(s_x, s_y)

    def test_vb_scale_2_preserve_aspect_ratio_meet_alignments(self):
        """ Test vb_scale_2 with different alignment values and meet behavior """
        # Use a narrower viewBox to create excess space for X alignment testing
        # viewBox: 50x100, document: 1.0x1.0 (1:1 aspect ratio)
        # viewBox aspect ratio is 1:2, document is 1:1
        # With "meet", scale limited by height, leaving excess width

        alignments = [
            "xMinYMin", "xMidYMin", "xMaxYMin",
            "xMinYMid", "xMidYMid", "xMaxYMid",
            "xMinYMax", "xMidYMax", "xMaxYMax"
        ]

        for alignment in alignments:
            with self.subTest(alignment=alignment):
                result = plot_utils.vb_scale_2("0 0 50 100", f"{alignment} meet", 1.0, 1.0)
                self.assertIsNotNone(result, f"Failed for alignment {alignment}")
                s_x, s_y, o_x, o_y = result

                # Should preserve aspect ratio
                self.assertEqual(s_x, s_y, f"Aspect ratio not preserved for {alignment}")

                # Scale limited by height (smaller scale factor)
                expected_scale = 1.0 / 100.0  # doc_height / vb_height (limiting dimension)
                self.assertAlmostEqual(s_x, expected_scale, places=6)

                # X offset should vary based on alignment
                # ViewBox scaled width = 50 * 0.01 = 0.5, doc width = 1.0, excess = 0.5
                if "xmin" in alignment.lower():
                    self.assertAlmostEqual(o_x, 0.0, places=6,
                                           msg=f"xMin offset wrong for {alignment}")
                elif "xmax" in alignment.lower():
                    # xMax: align to right edge, offset = excess_width = 50
                    self.assertAlmostEqual(o_x, 50.0, places=6,
                                           msg=f"xMax offset wrong for {alignment}")
                else:  # xMid
                    # xMid: center, offset = excess_width / 2 = 25
                    self.assertAlmostEqual(o_x, 25.0, places=6,
                                           msg=f"xMid offset wrong for {alignment}")

    def test_vb_scale_2_preserve_aspect_ratio_slice_alignments(self):
        """ Test vb_scale_2 with slice behavior """
        # Use same viewBox but with slice - should scale to fill, potentially cropping
        alignments = ["xMinYMin", "xMidYMid", "xMaxYMax"]

        for alignment in alignments:
            with self.subTest(alignment=alignment):
                result = plot_utils.vb_scale_2("0 0 200 100", f"{alignment} slice", 1.0, 1.0)
                self.assertIsNotNone(result, f"Failed for slice alignment {alignment}")
                s_x, s_y, o_x, o_y = result

                # Should preserve aspect ratio
                self.assertEqual(s_x, s_y, f"Aspect ratio not preserved for slice {alignment}")

                # With slice, scale limited by dimension that fills completely (height in this case)
                # Doc aspect ratio 1:1, viewBox aspect ratio 2:1 (wider)
                # Slice: scale so viewBox fills entire document (may crop)
                expected_scale = 1.0 / 100.0  # doc_height / vb_height (limiting dimension)
                self.assertAlmostEqual(s_x, expected_scale, places=6)

    def test_vb_scale_2_preserve_aspect_ratio_edge_cases(self):
        """ Test preserveAspectRatio edge cases """
        # Test case insensitivity
        result1 = plot_utils.vb_scale_2("0 0 100 100", "xMidYMid meet", 1.0, 1.0)
        result2 = plot_utils.vb_scale_2("0 0 100 100", "XMIDYMID MEET", 1.0, 1.0)
        self.assertEqual(result1, result2, "Case insensitivity failed")

        # Test with extra whitespace
        result3 = plot_utils.vb_scale_2("0 0 100 100", "  xMidYMid   meet  ", 1.0, 1.0)
        self.assertEqual(result1, result3, "Whitespace handling failed")

        # Test with only alignment parameter
        result4 = plot_utils.vb_scale_2("0 0 100 100", "xMinYMax", 1.0, 1.0)
        self.assertIsNotNone(result4, "Single parameter failed")

        # Test invalid preserveAspectRatio (should still work, fall back to defaults)
        result5 = plot_utils.vb_scale_2("0 0 100 100", "invalid", 1.0, 1.0)
        self.assertIsNotNone(result5, "Invalid preserveAspectRatio should still work")

    def test_vb_scale_2_preserve_aspect_ratio_square_viewbox(self):
        """ Test with square viewBox and rectangular document """
        # Square viewBox (100x100) in rectangular document (200x100)
        # Document aspect ratio 2:1, viewBox aspect ratio 1:1

        # With meet, should scale to fit the smaller dimension (height)
        result_meet = plot_utils.vb_scale_2("0 0 100 100", "xMidYMid meet", 2.0, 1.0)
        self.assertIsNotNone(result_meet)
        s_x, s_y, o_x, o_y = result_meet
        self.assertEqual(s_x, s_y)  # Aspect ratio preserved
        expected_scale = 1.0 / 100.0  # Limited by height
        self.assertAlmostEqual(s_x, expected_scale, places=6)

        # With slice, should scale to fill the larger dimension (width)
        result_slice = plot_utils.vb_scale_2("0 0 100 100", "xMidYMid slice", 2.0, 1.0)
        self.assertIsNotNone(result_slice)
        s_x, s_y, o_x, o_y = result_slice
        self.assertEqual(s_x, s_y)  # Aspect ratio preserved
        expected_scale = 2.0 / 100.0  # Limited by width
        self.assertAlmostEqual(s_x, expected_scale, places=6)

    def test_vb_scale_2_preserve_aspect_ratio_compatibility(self):
        """ Test that vb_scale_2 produces same results as vb_scale for preserveAspectRatio """
        test_cases = [
            ("0 0 100 100", None, 1.0, 1.0),
            ("0 0 100 100", "none", 2.0, 1.0),
            ("0 0 100 100", "xMinYMin meet", 1.0, 1.0),
            ("0 0 200 100", "xMidYMid slice", 1.0, 1.0),
            ("10 20 100 100", "xMaxYMax meet", 1.5, 1.0),
        ]

        for vb, par, doc_w, doc_h in test_cases:
            with self.subTest(viewBox=vb, preserveAspectRatio=par):
                result_original = plot_utils.vb_scale(vb, par, doc_w, doc_h)
                result_new = plot_utils.vb_scale_2(vb, par, doc_w, doc_h)
                self.assertIsNotNone(result_new, "vb_scale_2 returned None for valid case")
                self.assertEqual(result_original, result_new,
                                 f"Results differ for viewBox='{vb}', "
                                 f"preserveAspectRatio='{par}'")

    @staticmethod
    def get_random_points(num, seed=0):
        """ generate random (but deterministic) points where coords are between 0 and 1 """
        random.seed(seed)

        return [(random.random(), random.random()) for _ in range(num)]

    def test_clip_code_inside_bounds(self):
        """Test clip_code for point inside bounds"""
        # Point inside rectangular bounds
        code = plot_utils.clip_code(5, 5, 0, 10, 0, 10)
        self.assertEqual(code, 0)  # Inside = 0

    def test_clip_code_outside_bounds(self):
        """Test clip_code for points outside bounds"""
        # Test all boundary positions
        # Left (x < x_min)
        code = plot_utils.clip_code(-1, 5, 0, 10, 0, 10)
        self.assertEqual(code, 1)
        # Right (x > x_max)
        code = plot_utils.clip_code(15, 5, 0, 10, 0, 10)
        self.assertEqual(code, 2)
        # Top (y < y_min)
        code = plot_utils.clip_code(5, -1, 0, 10, 0, 10)
        self.assertEqual(code, 4)
        # Bottom (y > y_max)
        code = plot_utils.clip_code(5, 15, 0, 10, 0, 10)
        self.assertEqual(code, 8)

    def test_clip_code_corner_cases(self):
        """Test clip_code for corner positions"""
        # Top-left corner (left + top)
        code = plot_utils.clip_code(-1, -1, 0, 10, 0, 10)
        self.assertEqual(code, 5)  # 1 | 4 = 5
        # Top-right corner (right + top)
        code = plot_utils.clip_code(15, -1, 0, 10, 0, 10)
        self.assertEqual(code, 6)  # 2 | 4 = 6
        # Bottom-left corner (left + bottom)
        code = plot_utils.clip_code(-1, 15, 0, 10, 0, 10)
        self.assertEqual(code, 9)  # 1 | 8 = 9
        # Bottom-right corner (right + bottom)
        code = plot_utils.clip_code(15, 15, 0, 10, 0, 10)
        self.assertEqual(code, 10)  # 2 | 8 = 10

    def test_clip_code_boundary_points(self):
        """Test clip_code for points exactly on boundaries"""
        # Points exactly on boundaries should be inside (code = 0)
        bounds = (0, 10, 0, 10)  # x_min, x_max, y_min, y_max
        code = plot_utils.clip_code(0, 5, *bounds)
        self.assertEqual(code, 0)  # On left edge
        code = plot_utils.clip_code(10, 5, *bounds)
        self.assertEqual(code, 0)  # On right edge
        code = plot_utils.clip_code(5, 0, *bounds)
        self.assertEqual(code, 0)  # On top edge
        code = plot_utils.clip_code(5, 10, *bounds)
        self.assertEqual(code, 0)  # On bottom edge

    def test_clip_segment_entirely_inside(self):
        """Test clip_segment with segment entirely inside bounds"""
        segment = [[2, 3], [7, 8]]
        bounds = [[0, 0], [10, 10]]
        accept, result = plot_utils.clip_segment(segment, bounds)
        self.assertTrue(accept)
        self.assertEqual(result, segment)  # Should be unchanged

    def test_clip_segment_entirely_outside_same_side(self):
        """Test clip_segment with segment entirely outside on same side"""
        segment = [[-5, -3], [-2, -1]]  # Both points left of bounds
        bounds = [[0, 0], [10, 10]]
        accept, result = plot_utils.clip_segment(segment, bounds)
        self.assertFalse(accept)  # Should be rejected

    def test_clip_segment_crossing_single_boundary(self):
        """Test clip_segment crossing a single boundary"""
        # Horizontal line crossing left boundary
        segment = [[-2, 5], [5, 5]]
        bounds = [[0, 0], [10, 10]]
        accept, result = plot_utils.clip_segment(segment, bounds)
        self.assertTrue(accept)
        # First point should be clipped to x=0
        self.assertAlmostEqual(result[0][0], 0.0, places=6)
        self.assertAlmostEqual(result[0][1], 5.0, places=6)
        # Second point should be unchanged
        self.assertAlmostEqual(result[1][0], 5.0, places=6)
        self.assertAlmostEqual(result[1][1], 5.0, places=6)

    def test_clip_segment_crossing_multiple_boundaries(self):
        """Test clip_segment crossing multiple boundaries"""
        # Diagonal line crossing left and bottom boundaries
        segment = [[-2, -2], [5, 5]]
        bounds = [[0, 0], [10, 10]]
        accept, result = plot_utils.clip_segment(segment, bounds)
        self.assertTrue(accept)
        # Should be clipped to stay within bounds
        self.assertGreaterEqual(result[0][0], 0.0)
        self.assertGreaterEqual(result[0][1], 0.0)
        self.assertLessEqual(result[1][0], 10.0)
        self.assertLessEqual(result[1][1], 10.0)

    def test_clip_segment_vertical_line(self):
        """Test clip_segment with vertical line"""
        segment = [[5, -2], [5, 12]]  # Vertical line crossing top and bottom
        bounds = [[0, 0], [10, 10]]
        accept, result = plot_utils.clip_segment(segment, bounds)
        self.assertTrue(accept)
        # X coordinates should remain 5
        self.assertAlmostEqual(result[0][0], 5.0, places=6)
        self.assertAlmostEqual(result[1][0], 5.0, places=6)
        # Y coordinates should be clipped to bounds
        self.assertAlmostEqual(result[0][1], 0.0, places=6)
        self.assertAlmostEqual(result[1][1], 10.0, places=6)

    def test_clip_segment_horizontal_line(self):
        """Test clip_segment with horizontal line"""
        segment = [[-2, 5], [12, 5]]  # Horizontal line crossing left and right
        bounds = [[0, 0], [10, 10]]
        accept, result = plot_utils.clip_segment(segment, bounds)
        self.assertTrue(accept)
        # Y coordinates should remain 5
        self.assertAlmostEqual(result[0][1], 5.0, places=6)
        self.assertAlmostEqual(result[1][1], 5.0, places=6)
        # X coordinates should be clipped to bounds
        self.assertAlmostEqual(result[0][0], 0.0, places=6)
        self.assertAlmostEqual(result[1][0], 10.0, places=6)

    def test_units_to_user_units_basic(self):
        """Test unitsToUserUnits with basic units"""
        # No units or px - should return value unchanged
        result = plot_utils.unitsToUserUnits("100")
        self.assertAlmostEqual(result, 100.0, places=6)
        result = plot_utils.unitsToUserUnits("100px")
        self.assertAlmostEqual(result, 100.0, places=6)

    def test_units_to_user_units_inches(self):
        """Test unitsToUserUnits with inches"""
        # 1 inch = 96 pixels
        result = plot_utils.unitsToUserUnits("1in")
        self.assertAlmostEqual(result, 96.0, places=6)
        result = plot_utils.unitsToUserUnits("2.5in")
        self.assertAlmostEqual(result, 240.0, places=6)

    def test_units_to_user_units_metric(self):
        """Test unitsToUserUnits with metric units"""
        # 1mm = 96/25.4 pixels ≈ 3.7795 pixels
        result = plot_utils.unitsToUserUnits("25.4mm")
        self.assertAlmostEqual(result, 96.0, places=6)
        # 1cm = 96/2.54 pixels ≈ 37.7953 pixels
        result = plot_utils.unitsToUserUnits("2.54cm")
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_units_to_user_units_print_units(self):
        """Test unitsToUserUnits with print units (points, picas)"""
        # 1pt = 96/72 pixels = 4/3 pixels
        result = plot_utils.unitsToUserUnits("72pt")
        self.assertAlmostEqual(result, 96.0, places=6)
        # 1pc = 96/6 pixels = 16 pixels
        result = plot_utils.unitsToUserUnits("6pc")
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_units_to_user_units_quarter_millimeters(self):
        """Test unitsToUserUnits with quarter-millimeters"""
        # 1Q = 96/101.6 pixels (quarter-millimeter)
        result = plot_utils.unitsToUserUnits("101.6Q")
        self.assertAlmostEqual(result, 96.0, places=6)
        result = plot_utils.unitsToUserUnits("101.6q")
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_units_to_user_units_percentage(self):
        """Test unitsToUserUnits with percentage"""
        # With percent_ref
        result = plot_utils.unitsToUserUnits("50%", percent_ref=200)
        self.assertAlmostEqual(result, 100.0, places=6)
        # Without percent_ref
        result = plot_utils.unitsToUserUnits("75%")
        self.assertAlmostEqual(result, 0.75, places=6)

    def test_units_to_user_units_invalid(self):
        """Test unitsToUserUnits with invalid input"""
        # Invalid number
        result = plot_utils.unitsToUserUnits("invalid")
        self.assertIsNone(result)
        # Unsupported units
        result = plot_utils.unitsToUserUnits("100xyz")
        self.assertIsNone(result)

    def test_user_unit_to_units_basic(self):
        """Test userUnitToUnits with basic units"""
        # No units or px - should return value unchanged
        result = plot_utils.userUnitToUnits(100.0, "")
        self.assertAlmostEqual(result, 100.0, places=6)
        result = plot_utils.userUnitToUnits(100.0, "px")
        self.assertAlmostEqual(result, 100.0, places=6)

    def test_user_unit_to_units_inches(self):
        """Test userUnitToUnits with inches"""
        # 96 pixels = 1 inch
        result = plot_utils.userUnitToUnits(96.0, "in")
        self.assertAlmostEqual(result, 1.0, places=6)
        result = plot_utils.userUnitToUnits(240.0, "in")
        self.assertAlmostEqual(result, 2.5, places=6)

    def test_user_unit_to_units_metric(self):
        """Test userUnitToUnits with metric units"""
        # 96 pixels = 25.4 mm
        result = plot_utils.userUnitToUnits(96.0, "mm")
        self.assertAlmostEqual(result, 25.4, places=6)
        # 96 pixels = 2.54 cm
        result = plot_utils.userUnitToUnits(96.0, "cm")
        self.assertAlmostEqual(result, 2.54, places=6)

    def test_user_unit_to_units_print_units(self):
        """Test userUnitToUnits with print units"""
        # 96 pixels = 72 points
        result = plot_utils.userUnitToUnits(96.0, "pt")
        self.assertAlmostEqual(result, 72.0, places=6)
        # 96 pixels = 6 picas
        result = plot_utils.userUnitToUnits(96.0, "pc")
        self.assertAlmostEqual(result, 6.0, places=6)

    def test_user_unit_to_units_quarter_millimeters(self):
        """Test userUnitToUnits with quarter-millimeters"""
        # 96 pixels = 101.6 quarter-millimeters
        result = plot_utils.userUnitToUnits(96.0, "Q")
        self.assertAlmostEqual(result, 101.6, places=6)
        result = plot_utils.userUnitToUnits(96.0, "q")
        self.assertAlmostEqual(result, 101.6, places=6)

    def test_user_unit_to_units_percentage(self):
        """Test userUnitToUnits with percentage"""
        result = plot_utils.userUnitToUnits(0.5, "%")
        self.assertAlmostEqual(result, 50.0, places=6)

    def test_user_unit_to_units_invalid(self):
        """Test userUnitToUnits with invalid input"""
        # None input
        result = plot_utils.userUnitToUnits(None, "in")
        self.assertIsNone(result)
        # Unsupported units
        result = plot_utils.userUnitToUnits(100.0, "xyz")
        self.assertIsNone(result)


class MockSvgElement:
    """Mock SVG element for testing getLength and getLengthInches"""
    def __init__(self, attributes):
        self.attributes = attributes

    def get(self, name):
        return self.attributes.get(name)


class MockDocument:
    """Mock document for testing getLength and getLengthInches"""
    def __init__(self, root_attributes):
        self.root = MockSvgElement(root_attributes)

    def getroot(self):
        return self.root


class MockObject:
    """Mock object with document attribute for testing"""
    def __init__(self, root_attributes):
        self.document = MockDocument(root_attributes)


class GetLengthTestCase(unittest.TestCase):
    """Tests for getLength and getLengthInches functions"""

    def test_get_length_pixels(self):
        """Test getLength with pixel units"""
        mock_obj = MockObject({"width": "100px"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        self.assertAlmostEqual(result, 100.0, places=6)

    def test_get_length_no_units(self):
        """Test getLength with no units"""
        mock_obj = MockObject({"width": "150"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        self.assertAlmostEqual(result, 150.0, places=6)

    def test_get_length_inches(self):
        """Test getLength with inches"""
        mock_obj = MockObject({"width": "2in"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        # 2 inches * 96 px/inch = 192 px
        self.assertAlmostEqual(result, 192.0, places=6)

    def test_get_length_millimeters(self):
        """Test getLength with millimeters"""
        mock_obj = MockObject({"width": "25.4mm"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        # 25.4mm = 1 inch = 96 px
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_get_length_centimeters(self):
        """Test getLength with centimeters"""
        mock_obj = MockObject({"width": "2.54cm"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        # 2.54cm = 1 inch = 96 px
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_get_length_points(self):
        """Test getLength with points"""
        mock_obj = MockObject({"width": "72pt"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        # 72pt = 1 inch = 96 px
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_get_length_picas(self):
        """Test getLength with picas"""
        mock_obj = MockObject({"width": "6pc"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        # 6pc = 1 inch = 96 px
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_get_length_quarter_millimeters(self):
        """Test getLength with quarter-millimeters"""
        mock_obj = MockObject({"width": "101.6Q"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        # 101.6Q = 1 inch = 96 px
        self.assertAlmostEqual(result, 96.0, places=6)

    def test_get_length_percentage(self):
        """Test getLength with percentage"""
        mock_obj = MockObject({"width": "50%"})
        result = plot_utils.getLength(mock_obj, "width", 200)
        # 50% of 200 = 100
        self.assertAlmostEqual(result, 100.0, places=6)

    def test_get_length_missing_attribute(self):
        """Test getLength with missing attribute returns default"""
        mock_obj = MockObject({})
        result = plot_utils.getLength(mock_obj, "width", 75)
        self.assertAlmostEqual(result, 75.0, places=6)

    def test_get_length_invalid_value(self):
        """Test getLength with invalid value"""
        mock_obj = MockObject({"width": "invalid"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        self.assertIsNone(result)

    def test_get_length_unsupported_units(self):
        """Test getLength with unsupported units"""
        mock_obj = MockObject({"width": "100xyz"})
        result = plot_utils.getLength(mock_obj, "width", 50)
        self.assertIsNone(result)

    def test_get_length_inches_basic(self):
        """Test getLengthInches with inch units"""
        mock_obj = MockObject({"width": "2.5in"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        self.assertAlmostEqual(result, 2.5, places=6)

    def test_get_length_inches_millimeters(self):
        """Test getLengthInches with millimeters"""
        mock_obj = MockObject({"width": "25.4mm"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 25.4mm = 1 inch
        self.assertAlmostEqual(result, 1.0, places=6)

    def test_get_length_inches_centimeters(self):
        """Test getLengthInches with centimeters"""
        mock_obj = MockObject({"width": "5.08cm"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 5.08cm = 2 inches
        self.assertAlmostEqual(result, 2.0, places=6)

    def test_get_length_inches_points(self):
        """Test getLengthInches with points"""
        mock_obj = MockObject({"width": "144pt"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 144pt = 2 inches
        self.assertAlmostEqual(result, 2.0, places=6)

    def test_get_length_inches_picas(self):
        """Test getLengthInches with picas"""
        mock_obj = MockObject({"width": "12pc"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 12pc = 2 inches
        self.assertAlmostEqual(result, 2.0, places=6)

    def test_get_length_inches_quarter_millimeters(self):
        """Test getLengthInches with quarter-millimeters"""
        mock_obj = MockObject({"width": "203.2Q"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 203.2Q = 2 inches
        self.assertAlmostEqual(result, 2.0, places=6)

    def test_get_length_inches_pixels(self):
        """Test getLengthInches with pixels"""
        mock_obj = MockObject({"width": "192px"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 192px = 2 inches (at 96 px/inch)
        self.assertAlmostEqual(result, 2.0, places=6)

    def test_get_length_inches_no_units(self):
        """Test getLengthInches with no units (treated as pixels)"""
        mock_obj = MockObject({"width": "96"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        # 96 units = 1 inch (at 96 px/inch)
        self.assertAlmostEqual(result, 1.0, places=6)

    def test_get_length_inches_missing_attribute(self):
        """Test getLengthInches with missing attribute"""
        mock_obj = MockObject({})
        result = plot_utils.getLengthInches(mock_obj, "width")
        self.assertIsNone(result)

    def test_get_length_inches_invalid_value(self):
        """Test getLengthInches with invalid value"""
        mock_obj = MockObject({"width": "invalid"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        self.assertIsNone(result)

    def test_get_length_inches_percentage_unsupported(self):
        """Test getLengthInches with percentage (unsupported)"""
        mock_obj = MockObject({"width": "50%"})
        result = plot_utils.getLengthInches(mock_obj, "width")
        self.assertIsNone(result)
