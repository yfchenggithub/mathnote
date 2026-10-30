"""Validate the displayed geometry independently of its area shortcut."""
import math
import unittest
from model import AreaModel


class C088GeometryTests(unittest.TestCase):
    def test_general_area_against_shoelace(self):
        for k in (.1, .5, 2 / 3, 1, 3):
            for x1 in (-6, -1.5, 1, 3, 6):
                for x2 in (-6, -3, -.5, .5, 1.5, 3, 6):
                    m = AreaModel(k, x1, x2)
                    ax, ay = m.A
                    bx, by = m.B
                    self.assertAlmostEqual(abs(ax * by - bx * ay) / 2, m.area)
                    self.assertAlmostEqual(ay, k * ax)
                    self.assertAlmostEqual(by, -k * bx)

    def test_split_and_intercept_all_signs(self):
        for x1 in (-6, -3, 1, 3, 6):
            for x2 in (-6, -1, 1, 1.5, 3, 6):
                m = AreaModel(2 / 3, x1, x2)
                c = m.intercept
                if c is None:
                    self.assertEqual(m.A[1], m.B[1])
                    with self.assertRaises(ValueError):
                        _ = m.split_areas
                    continue
                ax, ay = m.A
                bx, by = m.B
                self.assertAlmostEqual((ax - c) * by, (bx - c) * ay)
                p, q = m.split_areas
                actual = p + q if x1 * x2 > 0 else abs(p - q)
                self.assertAlmostEqual(actual, m.area)

    def test_every_displayed_motion_state(self):
        for i in range(1001):
            x2 = 1.5 + 1.5 * i / 1000
            m = AreaModel(2 / 3, 3, x2)
            self.assertTrue(x2 <= m.intercept <= 3)
            self.assertAlmostEqual(sum(m.split_areas), m.area)
            if x2 != 3:
                self.assertAlmostEqual((3 - m.intercept) / (m.intercept - x2), 3 / x2)

    def test_actual_key_numbers_and_curve_membership(self):
        initial = AreaModel(2 / 3, 3, 3)
        half = AreaModel(2 / 3, 3, 1.5)
        self.assertEqual(initial.area, 6)
        self.assertEqual(half.area, 3)
        self.assertEqual(half.intercept, 2)
        self.assertEqual(half.split_areas, (2, 1))
        # A and B are asymptote points, never points of x^2/9-y^2/4=1.
        for x, y in (half.A, half.B):
            self.assertAlmostEqual(x * x / 9 - y * y / 4, 0)
        for t in (-1.05, -.5, 0, .5, 1.05):
            x, y = 3 * math.cosh(t), 2 * math.sinh(t)
            self.assertAlmostEqual(x * x / 9 - y * y / 4, 1)

    def test_invalid_parameters(self):
        for p in ((0, 3, 1), (-1, 3, 1), (1, 0, 1), (1, 1, 0), (float('nan'), 1, 1)):
            with self.assertRaises(ValueError):
                AreaModel(*p)


if __name__ == '__main__':
    unittest.main()
