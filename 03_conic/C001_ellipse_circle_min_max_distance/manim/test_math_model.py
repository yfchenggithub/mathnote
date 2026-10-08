"""Run with: python -m unittest discover -s <C001>/manim -p test_math_model.py"""

import math
import unittest

from math_model import (
    center_distance_range,
    circle_point,
    ellipse_point,
    farthest_pair,
    intersection_points,
    maximum_distance,
    minimum_distance,
    nearest_pair,
    on_circle,
    on_ellipse,
)


class GeometryTests(unittest.TestCase):
    def test_center_extrema_independent_sampling(self):
        distances = [math.dist(ellipse_point(2 * math.pi * i / 20000), (4, 0)) for i in range(20000)]
        self.assertEqual(center_distance_range(), (1, 7))
        self.assertAlmostEqual(min(distances), 1, places=7)
        self.assertAlmostEqual(max(distances), 7, places=7)

    def test_geometry_and_extremal_pairs(self):
        radii = [0.5, 1, 2, 4, 7, 8, 1 - 1e-5, 1 + 1e-5, 7 - 1e-5, 7 + 1e-5]
        for r in radii:
            with self.subTest(radius=r):
                p, q = nearest_pair(r)
                self.assertTrue(on_ellipse(p))
                self.assertTrue(on_circle(q, r))
                self.assertAlmostEqual(math.dist(p, q), minimum_distance(r), places=7)
                p, q = farthest_pair(r)
                self.assertTrue(on_ellipse(p))
                self.assertTrue(on_circle(q, r))
                self.assertAlmostEqual(math.dist(p, q), maximum_distance(r), places=7)
                for point in intersection_points(r):
                    self.assertTrue(on_ellipse(point))
                    self.assertTrue(on_circle(point, r))
                self.assertEqual(bool(intersection_points(r)), 1 <= r <= 7)

    def test_boundary_and_intersection_shape(self):
        self.assertEqual(intersection_points(1), ((3, 0),))
        self.assertEqual(intersection_points(7), ((-3, 0),))
        self.assertEqual(len(intersection_points(4)), 2)
        self.assertEqual(intersection_points(0.5), ())
        self.assertEqual(intersection_points(8), ())

    def test_parametric_points(self):
        for i in range(36):
            t = 2 * math.pi * i / 36
            self.assertTrue(on_ellipse(ellipse_point(t)))
            self.assertTrue(on_circle(circle_point(3.5, t), 3.5))

    def test_positive_radius_required(self):
        with self.assertRaises(ValueError):
            minimum_distance(0)
        with self.assertRaises(ValueError):
            intersection_points(-1)


if __name__ == "__main__":
    unittest.main()
