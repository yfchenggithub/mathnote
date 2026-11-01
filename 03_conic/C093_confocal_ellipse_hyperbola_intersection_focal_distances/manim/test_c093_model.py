import math
import unittest

from c093_model import ConfocalConics


class ConfocalModelTests(unittest.TestCase):
    def test_formal_examples(self):
        for a, c, A, expected in [(4, 2, 1, (5, 3)),
                                  (5, 3, 2, (7, 3)),
                                  (7, 4, 2, (9, 5))]:
            m = ConfocalConics(a, c, A)
            for actual, wanted in zip(m.distances(), expected):
                self.assertAlmostEqual(actual, wanted, places=12)

    def test_entire_animated_parameter_interval_and_four_points(self):
        for i in range(1001):
            m = ConfocalConics(A=0.6 + 0.9*i/1000)
            self.assertAlmostEqual(m.a**2-m.b**2, m.c**2, places=12)
            self.assertAlmostEqual(m.A**2+m.B**2, m.c**2, places=12)
            for branch in (-1, 1):
                for vertical in (-1, 1):
                    p = m.intersection(branch, vertical)
                    for residual in m.residuals(p):
                        self.assertAlmostEqual(residual, 0, places=11)
                    r1, r2 = m.distances(branch, vertical)
                    e1, e2 = m.expected_distances(branch)
                    self.assertAlmostEqual(r1, e1, places=11)
                    self.assertAlmostEqual(r2, e2, places=11)
                    self.assertAlmostEqual(r1+r2, 2*m.a, places=11)
                    self.assertAlmostEqual(abs(r1-r2), 2*m.A, places=11)
                    self.assertAlmostEqual(r1*r1-r2*r2, 4*m.c*p[0], places=11)

    def test_curves_and_viewport_at_every_output_parameter(self):
        for i in range(301):
            m = ConfocalConics(A=0.6 + 0.9*i/300)
            limit = m.visible_hyperbola_y_limit()
            for y in (-limit, -limit/2, 0, limit/2, limit):
                for branch in (-1, 1):
                    p = m.hyperbola_point(y, branch)
                    self.assertAlmostEqual(m.residuals(p)[1], 0, places=11)
                    self.assertLessEqual(abs(p[0]), 4.5+1e-10)
                    self.assertLessEqual(abs(p[1]), 3.65+1e-10)

    def test_near_boundaries(self):
        for a, c, A in [(2.00001, 2, 0.00001), (4, 2, 1.99999),
                        (3.00001, 3, 2.99999)]:
            m = ConfocalConics(a, c, A)
            for branch in (-1, 1):
                self.assertGreater(min(m.distances(branch)), 0)
                for residual in m.residuals(m.intersection(branch)):
                    self.assertAlmostEqual(residual, 0, places=8)

    def test_invalid_conditions_rejected(self):
        for a, c, A in [(2, 2, 1), (4, 2, 2), (4, 2, 0),
                        (4, 0, 1), (4, 2, -1), (math.inf, 2, 1),
                        (4, math.nan, 1)]:
            with self.assertRaises(ValueError):
                ConfocalConics(a, c, A)
        with self.assertRaises(ValueError):
            ConfocalConics().intersection(0)


if __name__ == "__main__":
    unittest.main()
