"""Independent analytic and numerical checks for the C002 lesson."""

import math
import unittest

from math_model import (A, B, NORMAL, R, SEMIMAJOR, SEMIMINOR,
                        ellipse_value, line_value, state)


class DistanceModelTests(unittest.TestCase):
    def test_support_and_formula_at_representative_states(self):
        for c in (0.0, 2.0, R - .001, R, R + .001, 10.0):
            with self.subTest(c=c):
                s = state(c)
                for point in (s.near, s.far):
                    self.assertAlmostEqual(ellipse_value(point), 1.0, places=12)
                self.assertAlmostEqual(line_value(s.near, 0), -R, places=12)
                self.assertAlmostEqual(line_value(s.far, 0), R, places=12)
                self.assertAlmostEqual(math.dist(s.far, s.far_foot), s.d_max, places=12)
                self.assertAlmostEqual(line_value(s.far_foot, c), 0, places=12)
                self.assertAlmostEqual(line_value(s.near_foot, c), 0, places=12)
                self.assertAlmostEqual(s.d_max, (c + R) / NORMAL, places=12)
                if s.relation == "separate":
                    self.assertEqual(len(s.intersections), 0)
                    self.assertAlmostEqual(math.dist(s.near, s.near_foot), s.d_min, places=12)
                else:
                    self.assertEqual(len(s.intersections), 1 if s.relation == "tangent" else 2)
                    self.assertEqual(s.d_min, 0)
                for point in s.intersections:
                    self.assertAlmostEqual(ellipse_value(point), 1.0, places=10)
                    self.assertAlmostEqual(line_value(point, c), 0, places=10)

    def test_extrema_against_independent_dense_scan(self):
        # This evaluates the original point-to-line formula, not state().
        for c in (0.0, 2.0, R, 10.0):
            distances = [abs(A * SEMIMAJOR * math.cos(2 * math.pi * i / 20000)
                             + B * SEMIMINOR * math.sin(2 * math.pi * i / 20000)
                             + c) / NORMAL for i in range(20000)]
            s = state(c)
            self.assertAlmostEqual(max(distances), s.d_max, delta=0.0002)
            self.assertAlmostEqual(min(distances), s.d_min, delta=0.0002)

    def test_invalid_negative_c(self):
        with self.assertRaises(ValueError):
            state(-1)


if __name__ == "__main__":
    unittest.main()
