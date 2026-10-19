import unittest
from math import asin, cos, pi, tan
from model import Ellipse


class GeometryTests(unittest.TestCase):
    def test_geometry_and_half_angle_across_shapes(self):
        for a, b in [(3, 2), (2, 3**0.5), (5, 4.999), (5, 0.1)]:
            e = Ellipse(a, b)
            for i in range(721):
                t = i * pi / 360
                x, y = e.point(t)
                self.assertAlmostEqual(x*x/a**2 + y*y/b**2, 1, places=12)
                self.assertAlmostEqual(e.focal_sum(t), 2*a, places=11)
                self.assertAlmostEqual(tan(e.angle(t)/2), e.half_tangent(t), places=8)
                self.assertLessEqual(e.angle(t), e.maximum + 1e-12)
                expected = (b**4-e.c**2*y*y)/(b**4+e.c**2*y*y)
                self.assertAlmostEqual(cos(e.angle(t)), expected, places=10)

    def test_both_maxima_and_zero_endpoints(self):
        e = Ellipse()
        for t in (pi/2, 3*pi/2):
            self.assertAlmostEqual(e.angle(t), e.maximum, places=12)
        for t in (0, pi, 2*pi):
            self.assertAlmostEqual(e.angle(t), 0, places=12)
        self.assertAlmostEqual(e.maximum, 2*asin(e.c/e.a), places=12)

    def test_monotonicity_and_reflection(self):
        e = Ellipse()
        values = [e.angle(i*pi/200) for i in range(101)]
        self.assertTrue(all(v > u for u, v in zip(values, values[1:])))
        for i in range(101):
            t = i*pi/100
            self.assertAlmostEqual(e.angle(t), e.angle(-t), places=12)

    def test_formal_examples_and_reject_wrong_formula(self):
        e = Ellipse(2, 3**0.5)
        self.assertAlmostEqual(e.maximum, pi/3, places=12)
        e = Ellipse(5**0.5, 2)
        self.assertAlmostEqual(e.half_tangent(pi/6), 0.25, places=12)
        self.assertNotAlmostEqual(e.half_tangent(pi/6), e.c/abs(e.point(pi/6)[1]))

    def test_invalid_shapes(self):
        for a, b in [(1, 1), (1, 2), (1, 0), (-1, -2)]:
            with self.assertRaises(ValueError):
                Ellipse(a, b)


if __name__ == '__main__':
    unittest.main()
