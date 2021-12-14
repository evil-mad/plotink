"""
Tests for text_utils.py

part of https://github.com/evil-mad/plotink

"""

import unittest

from plotink import text_utils

# python -m unittest discover in top-level package dir

# pylint: disable=too-many-public-methods


class TextUtilsTestCase(unittest.TestCase):
    """
    Unit tests for text_utils.py
    """

    def test_format_hms(self):
        """ test format_hms function """
        self.assertEqual(text_utils.format_hms(3600),
            '1:00:00 (Hours, minutes, seconds)')
        self.assertEqual(text_utils.format_hms(3600.00),
            '1:00:00 (Hours, minutes, seconds)')
        self.assertEqual(text_utils.format_hms(3600.00, False),
            '1:00:00 (Hours, minutes, seconds)')
        self.assertEqual(text_utils.format_hms(3600.00, milliseconds=False),
            '1:00:00 (Hours, minutes, seconds)')
        self.assertEqual(text_utils.format_hms(3600.00, milliseconds=True),
            '3.600 Seconds')
        self.assertEqual(text_utils.format_hms(12345.67890, True),
            '12 Seconds')
        self.assertEqual(text_utils.format_hms(12345.67890, milliseconds=True),
            '12 Seconds')
        self.assertEqual(text_utils.format_hms(12345.67890),
            '3:25:46 (Hours, minutes, seconds)')
        self.assertEqual(text_utils.format_hms(1.23456),
            '1.235 Seconds')
        self.assertEqual(text_utils.format_hms(3.123456),
            '3.123 Seconds')
        self.assertEqual(text_utils.format_hms(65),
            '1:05 (Minutes, seconds)')
        self.assertEqual(text_utils.format_hms(3500),
            '58:20 (Minutes, seconds)')
        self.assertEqual(text_utils.format_hms(1.0456e7),
            '2904:26:40 (Hours, minutes, seconds)')
        self.assertEqual(text_utils.format_hms(9.999),
            '9.999 Seconds')
        self.assertEqual(text_utils.format_hms(9999, True),
            '9.999 Seconds')
        self.assertEqual(text_utils.format_hms(10.0001),
            '10 Seconds')
        self.assertEqual(text_utils.format_hms(10.49),
            '10 Seconds')
        self.assertEqual(text_utils.format_hms(10.51),
            '11 Seconds')
        self.assertEqual(text_utils.format_hms(179.999),
            '3:00 (Minutes, seconds)')
        self.assertEqual(text_utils.format_hms(179.49),
            '2:59 (Minutes, seconds)')
        self.assertEqual(text_utils.format_hms(180.49),
            '3:00 (Minutes, seconds)')
        self.assertEqual(text_utils.format_hms(3599.6),
            '1:00:00 (Hours, minutes, seconds)')


    def test_xml_escape(self):
        """ test xml_escape function """
        self.assertEqual(text_utils.xml_escape("Hello&Goodbye"),
            'Hello&amp;Goodbye')
        self.assertEqual(text_utils.xml_escape("<test>"),
            '&lt;test&gt;')
        self.assertEqual(text_utils.xml_escape("The sun's out today"),
            'The sun&apos;s out today')
        self.assertEqual(text_utils.xml_escape('"Lemon Pie"'),
            '&quot;Lemon Pie&quot;')
