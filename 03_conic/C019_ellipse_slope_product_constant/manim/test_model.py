import unittest
from math import pi, sin, cos, sqrt, isfinite
from model import SlopeProductModel


class SlopeProductTests(unittest.TestCase):
    def test_domain(self):
        for args in ((3, 4), (3, 3), (4, 0), (float('nan'), 3)):
            with self.assertRaises(ValueError):
                SlopeProductModel(*args)

    def test_formal_example(self):
        model = SlopeProductModel()
        x, y = model.point(pi/3)
        self.assertAlmostEqual(x, 2)
        self.assertAlmostEqual(y, 3*sqrt(3)/2)
        r, t = model.slopes(pi/3)
        self.assertAlmostEqual(r, 3*sqrt(3)/4)
        self.assertAlmostEqual(t, -sqrt(3)/4)
        self.assertAlmostEqual(model.measured_product(pi/3), -9/16)

    def test_product_all_quadrants(self):
        for a, b in ((4, 3), (5, 2), (2, .7)):
            model = SlopeProductModel(a, b)
            for i in range(720):
                theta = (i+.5)*pi/360
                r, t = model.slopes(theta)
                self.assertLess(r*t, 0)
                self.assertAlmostEqual(r*t, model.constant)
                self.assertAlmostEqual(r*t, model.eccentricity**2-1)

    def test_curve_tangent_and_direction(self):
        model = SlopeProductModel()
        for i in range(721):
            theta = i*pi/360
            x, y = model.point(theta)
            A, B, C = model.tangent(theta)
            self.assertAlmostEqual(x*x/16+y*y/9, 1)
            self.assertAlmostEqual(A*x+B*y, C)
            self.assertAlmostEqual(A*(-4*sin(theta))+B*(3*cos(theta)), 0)

    def test_axis_product_rejected(self):
        model = SlopeProductModel()
        for theta in (0, pi/2, pi, 3*pi/2, 2*pi):
            with self.assertRaises(ValueError):
                model.measured_product(theta)

    def test_near_axes_are_valid(self):
        model = SlopeProductModel()
        for theta in (1e-7, pi/2-1e-7, pi+1e-7, 3*pi/2+1e-7):
            self.assertTrue(all(isfinite(v) for v in model.slopes(theta)))
            self.assertAlmostEqual(model.measured_product(theta), -9/16)

    def test_animation_interval(self):
        model = SlopeProductModel()
        for i in range(1001):
            theta = (20+i*.05)*pi/180
            x, y = model.point(theta)
            radial, tangent = model.slopes(theta)
            self.assertGreater(x, 1)
            self.assertGreater(y, 1)
            self.assertGreater(radial, 0)
            self.assertLess(tangent, 0)
            self.assertLess(max(abs(radial), abs(tangent)), 2.1)

    def test_clipping(self):
        model = SlopeProductModel()
        for i in range(721):
            theta = i*pi/360
            A, B, C = model.tangent(theta)
            ends = model.clipped_tangent(theta)
            self.assertEqual(len(ends), 2)
            for x, y in ends:
                self.assertAlmostEqual(A*x+B*y, C)
                self.assertLessEqual(abs(x), 4.8+1e-9)
                self.assertLessEqual(abs(y), 4.2+1e-9)

    def test_independent_parametric_derivative(self):
        model = SlopeProductModel()
        for degrees in (20, 35, 60, 70, 120, 200, 320):
            theta = degrees*pi/180
            radial, tangent = model.slopes(theta)
            self.assertAlmostEqual(tangent, 3*cos(theta)/(-4*sin(theta)))

    def test_radial_not_normal(self):
        model = SlopeProductModel()
        x, y = model.point(pi/3)
        A, B, _ = model.tangent(pi/3)
        self.assertNotAlmostEqual(x*B-y*A, 0)
        self.assertNotAlmostEqual(model.measured_product(pi/3), -1)


if __name__ == '__main__':
    unittest.main()
