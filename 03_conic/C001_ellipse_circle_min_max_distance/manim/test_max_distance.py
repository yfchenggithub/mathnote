"""Regression checks for the independent maximum-distance animation."""

import math
import unittest

from math_model import (
    M, center_distance_range, ellipse_point, farthest_pair,
    maximum_distance, on_circle, on_ellipse,
)


class MaximumDistanceTests(unittest.TestCase):
    def test_ellipse_center_maximum(self):
        self.assertEqual(center_distance_range()[1], 7)
        samples = [ellipse_point(2 * math.pi * i / 20000)
                   for i in range(20000)]
        self.assertAlmostEqual(max(math.dist(point, M) for point in samples), 7)

    def test_extremal_pair_at_required_radii(self):
        for radius in (0.5, 1, 2, 4, 7, 8):
            with self.subTest(radius=radius):
                p, q = farthest_pair(radius)
                self.assertEqual(p, (-3, 0))
                self.assertEqual(q, (4 + radius, 0))
                self.assertTrue(on_ellipse(p))
                self.assertTrue(on_circle(q, radius))
                self.assertAlmostEqual(math.dist(p, q), 7 + radius)
                self.assertAlmostEqual(maximum_distance(radius), 7 + radius)
                self.assertAlmostEqual(math.dist(p, q), maximum_distance(radius))

    def test_no_other_sampled_pair_is_farther(self):
        # Independent grid search checks the two-curve maximum, not only the
        # formula implementation shared with the displayed number.
        for radius in (0.5, 2, 4, 8):
            candidate = maximum_distance(radius)
            for i in range(120):
                p = ellipse_point(2 * math.pi * i / 120)
                for j in range(120):
                    angle = 2 * math.pi * j / 120
                    q = (M[0] + radius * math.cos(angle),
                         M[1] + radius * math.sin(angle))
                    self.assertLessEqual(math.dist(p, q), candidate + 1e-10)

    def test_positive_radius(self):
        with self.assertRaises(ValueError):
            maximum_distance(0)


if __name__ == "__main__":
    unittest.main()
