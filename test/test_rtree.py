"""
Tests for rtree.py

part of https://github.com/evil-mad/plotink

"""

import random
import unittest

from plotink import rtree

# python -m unittest discover in top-level package dir


def brute_force(bboxes, query):
    """ IDs of bboxes that intersect query, by direct comparison """
    x_1, y_1, x_2, y_2 = query
    return {i for (i, (xmin, ymin, xmax, ymax)) in bboxes
            if not (x_1 > xmax or y_1 > ymax or x_2 < xmin or y_2 < ymin)}


def count_nodes(index):
    """ Number of nodes in an index tree """
    return 1 + sum(count_nodes(subt) for subt in index.subtrees)


def count_entries(index):
    """ Number of stored bbox entries, including duplicates across nodes """
    return len(index.bboxes) + sum(count_entries(subt) for subt in index.subtrees)


class RTreeTestCase(unittest.TestCase):
    """
    Tests for rtree.py
    """

    def test_zero_width_boxes_on_split_line(self):
        """ Vertical segments sharing one x value are all found """
        bboxes = [(i, (5.0, float(i), 5.0, float(i) + 0.5)) for i in range(10)]
        index = rtree.Index(bboxes)
        self.assertEqual(index.intersection((0.0, 0.0, 10.0, 20.0)), set(range(10)))

    def test_zero_height_boxes_on_split_line(self):
        """ Horizontal segments sharing one y value are all found """
        bboxes = [(i, (float(i), 5.0, float(i) + 0.5, 5.0)) for i in range(10)]
        index = rtree.Index(bboxes)
        self.assertEqual(index.intersection((0.0, 0.0, 20.0, 10.0)), set(range(10)))

    def test_point_boxes(self):
        """ Zero-size boxes, including coincident ones, are all found """
        bboxes = [(i, (float(i % 3), float(i % 3), float(i % 3), float(i % 3)))
                  for i in range(9)]
        index = rtree.Index(bboxes)
        self.assertEqual(index.intersection((0.0, 0.0, 2.0, 2.0)), set(range(9)))
        self.assertEqual(index.intersection((1.0, 1.0, 1.0, 1.0)), {1, 4, 7})

    def test_empty_index(self):
        """ An index with no boxes returns no matches """
        self.assertEqual(rtree.Index([]).intersection((0, 0, 1, 1)), set())

    def test_matches_brute_force(self):
        """ Query results match direct comparison for mixed box shapes """
        rng = random.Random(1)
        bboxes = []
        for i in range(600):
            kind = i % 4
            x, y = rng.uniform(0, 100), rng.uniform(0, 100)
            if kind == 0:    # vertical segment, often on a shared x
                x = float(rng.choice([25, 50, 75])) if rng.random() < 0.5 else x
                bboxes.append((i, (x, y, x, y + rng.uniform(0, 10))))
            elif kind == 1:  # horizontal segment, often on a shared y
                y = float(rng.choice([25, 50, 75])) if rng.random() < 0.5 else y
                bboxes.append((i, (x, y, x + rng.uniform(0, 10), y)))
            elif kind == 2:  # small box
                bboxes.append((i, (x, y, x + rng.uniform(0, 5), y + rng.uniform(0, 5))))
            else:            # large box
                bboxes.append((i, (x - 40, y - 40, x + rng.uniform(0, 60),
                                   y + rng.uniform(0, 60))))
        index = rtree.Index(bboxes)
        for _ in range(200):
            x, y = rng.uniform(-10, 110), rng.uniform(-10, 110)
            query = (x, y, x + rng.uniform(0, 30), y + rng.uniform(0, 30))
            self.assertEqual(index.intersection(query), brute_force(bboxes, query))

    def test_large_overlapping_boxes_stay_compact(self):
        """ Many large, overlapping boxes do not cause runaway duplication """
        rng = random.Random(1)
        bboxes = []
        for i in range(2500):
            x, y = rng.uniform(0, 800), rng.uniform(0, 800)
            w, h = rng.uniform(100, 600), rng.uniform(100, 600)
            bboxes.append((i, (x - w / 2, y - h / 2, x + w / 2, y + h / 2)))
        index = rtree.Index(bboxes)
        self.assertLess(count_entries(index), 4 * len(bboxes))
        self.assertLess(count_nodes(index), len(bboxes))
        query = (300, 300, 320, 320)
        self.assertEqual(index.intersection(query), brute_force(bboxes, query))


if __name__ == '__main__':
    unittest.main()
