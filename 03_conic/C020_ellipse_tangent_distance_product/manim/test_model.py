import unittest
from math import pi, sqrt, sin, cos, hypot
from model import DistanceProductModel


class DistanceProductTests(unittest.TestCase):
    def test_domain(self):
        for args in ((3, 4), (3, 3), (4, 0), (float('inf'), 3)):
            with self.assertRaises(ValueError):
                DistanceProductModel(*args)

    def test_formal_example(self):
        state = DistanceProductModel().state(pi/3)
        self.assertAlmostEqual(state['p'][0], 2)
        self.assertAlmostEqual(state['p'][1], 3*sqrt(3)/2)
        self.assertAlmostEqual(state['r1'], 4+sqrt(7)/2)
        self.assertAlmostEqual(state['r2'], 4-sqrt(7)/2)
        self.assertAlmostEqual(state['r1']*state['r2'], 57/4)
        self.assertAlmostEqual(state['d'], 24/sqrt(57))

    def test_full_curve_and_tangent(self):
        model = DistanceProductModel()
        for i in range(1441):
            t = i*pi/720
            x, y = model.point(t)
            A, B, C = model.tangent(t)
            self.assertAlmostEqual(x*x/16+y*y/9, 1)
            self.assertAlmostEqual(A*x+B*y, C)
            self.assertAlmostEqual(A*(-4*sin(t))+B*(3*cos(t)), 0)

    def test_projection_is_perpendicular_and_on_line(self):
        model = DistanceProductModel()
        for i in range(721):
            t = i*pi/360
            s = model.state(t)
            hx, hy = s['h']
            A, B, C = model.tangent(t)
            self.assertAlmostEqual(A*hx+B*hy, C)
            self.assertAlmostEqual(hx*(-B)+hy*A, 0)
            self.assertAlmostEqual(s['d'], 1/hypot(A, B))

    def test_invariant_three_ellipses_all_quadrants(self):
        for a, b in ((4, 3), (5, 4), (5, 2)):
            model = DistanceProductModel(a, b)
            for i in range(721):
                s = model.state(i*pi/360)
                self.assertAlmostEqual(s['r1']+s['r2'], 2*a)
                self.assertAlmostEqual(s['product'], a*b)
                self.assertAlmostEqual(s['r1']*s['r2']*s['d']**2, a*a*b*b)
                self.assertGreaterEqual(s['d'], b-1e-10)
                self.assertLessEqual(s['d'], a+1e-10)
                self.assertGreaterEqual(s['geometric_mean'], b-1e-10)
                self.assertLessEqual(s['geometric_mean'], a+1e-10)

    def test_independent_parameter_factor(self):
        model = DistanceProductModel()
        for i in range(361):
            t = i*pi/180
            s = model.state(t)
            factor = 9*cos(t)**2+16*sin(t)**2
            self.assertAlmostEqual(s['r1']*s['r2'], factor)
            self.assertAlmostEqual(s['d'], 12/sqrt(factor))

    def test_vertices(self):
        model = DistanceProductModel()
        for t, d, g in ((0, 4, 3), (pi/2, 3, 4), (pi, 4, 3), (3*pi/2, 3, 4)):
            s = model.state(t)
            self.assertAlmostEqual(s['d'], d)
            self.assertAlmostEqual(s['geometric_mean'], g)
            self.assertAlmostEqual(hypot(s['h'][0]-s['p'][0], s['h'][1]-s['p'][1]), 0)

    def test_updated_feasible_example(self):
        model = DistanceProductModel(5, 4)
        # x=5sqrt(5)/3, y=8/3 corresponds to sin(t)=2/3.
        from math import asin
        s = model.state(asin(2/3))
        self.assertAlmostEqual(s['d'], 2*sqrt(5))
        self.assertAlmostEqual(s['r1']*s['r2'], 20)
        self.assertLess(2, model.b)  # Updated LaTeX identifies the old d=2 as impossible.

    def test_geometric_half_angle(self):
        model = DistanceProductModel()
        for i in range(181):
            s = model.state(i*pi/180)
            cosine = (s['r1']**2+s['r2']**2-4*model.c**2)/(2*s['r1']*s['r2'])
            half_cosine = sqrt(max(0, (1+cosine)/2))
            self.assertAlmostEqual(s['d'], model.a*half_cosine)

    def test_clipping(self):
        model = DistanceProductModel()
        for i in range(721):
            t = i*pi/360
            A, B, C = model.tangent(t)
            ends = model.clipped_tangent(t)
            self.assertEqual(len(ends), 2)
            for x, y in ends:
                self.assertAlmostEqual(A*x+B*y, C)
                self.assertLessEqual(abs(x), 5+1e-9)
                self.assertLessEqual(abs(y), 4.35+1e-9)


if __name__ == '__main__':
    unittest.main()
