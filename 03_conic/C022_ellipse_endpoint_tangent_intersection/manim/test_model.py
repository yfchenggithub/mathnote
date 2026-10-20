import unittest
from math import pi, acos, cos, sin, sqrt
from model import EndpointModel


class EndpointIntersectionTests(unittest.TestCase):
    def test_domain(self):
        for args in ((2, 3), (3, 3), (3, 0), (float('nan'), 2)):
            with self.assertRaises(ValueError):
                EndpointModel(*args)

    def test_major_axis_vertices_excluded(self):
        for t in (0, pi, 2*pi):
            with self.assertRaises(ValueError):
                EndpointModel().state(t)

    def test_formal_sloped_example(self):
        s = EndpointModel().state(acos(-.6))
        self.assertAlmostEqual(s['k'], .5)
        self.assertAlmostEqual(s['m'], 2.5)
        self.assertAlmostEqual(s['h1'], 1)
        self.assertAlmostEqual(s['h2'], 4)
        self.assertAlmostEqual(s['area'], 15)

    def test_general_intersections_and_tangency(self):
        for a, b in ((3, 2), (4, 3), (2, .7)):
            model = EndpointModel(a, b)
            for i in range(720):
                t = (i+.5)*pi/360
                s = model.state(t)
                x, y = s['p']
                A, B = x/a**2, y/b**2
                self.assertAlmostEqual(x*x/a**2+y*y/b**2, 1)
                for qx, qy in (s['p'], s['p1'], s['p2']):
                    self.assertAlmostEqual(A*qx+B*qy, 1)
                self.assertAlmostEqual(A*(-a*sin(t))+B*(b*cos(t)), 0)
                self.assertGreater(s['p1'][1]*s['p2'][1], 0)
                self.assertAlmostEqual(s['product'], b*b, places=8)
                self.assertAlmostEqual(s['m']**2-a*a*s['k']**2, b*b, places=7)

    def test_area_formula_both_halves(self):
        model = EndpointModel()
        for i in range(720):
            t = (i+.5)*pi/360
            s = model.state(t)
            self.assertAlmostEqual(s['area'], 3*(s['h1']+s['h2']))
            self.assertAlmostEqual(s['area'], 6*abs(s['m']))
            self.assertAlmostEqual(s['area'], 24/abs(s['p'][1]))
            self.assertGreaterEqual(s['area'], 12-1e-10)

    def test_equality_at_both_short_axis_vertices(self):
        for t in (pi/2, 3*pi/2):
            s = EndpointModel().state(t)
            self.assertAlmostEqual(s['h1'], 2)
            self.assertAlmostEqual(s['h2'], 2)
            self.assertAlmostEqual(s['area'], 12)
            self.assertAlmostEqual(s['k'], 0)

    def test_animation_range_fits_view(self):
        model = EndpointModel()
        left, right = acos(.6), acos(-.6)
        for i in range(1001):
            s = model.state(left+(right-left)*i/1000)
            for h in (s['h1'], s['h2']):
                self.assertGreaterEqual(h, 1-1e-10)
                self.assertLessEqual(h, 4+1e-10)
            self.assertGreaterEqual(s['area'], 12-1e-10)
            self.assertLessEqual(s['area'], 15+1e-10)
            for x, y in model.tangent_ends(left+(right-left)*i/1000):
                self.assertLessEqual(abs(x), 3.6)
                self.assertGreaterEqual(y, .7-1e-10)
                self.assertLessEqual(y, 4.3+1e-10)

    def test_half_angle_independent_check(self):
        model = EndpointModel()
        for t in (.4, .8, pi/2, 2.3, 3.7, 5.6):
            s = model.state(t)
            from math import tan
            self.assertAlmostEqual(s['h1'], abs(2/tan(t/2)))
            self.assertAlmostEqual(s['h2'], abs(2*tan(t/2)))

    def test_endpoints_have_no_finite_area_maximum(self):
        model = EndpointModel()
        areas = [model.state(t)['area'] for t in (.2, .02, .002)]
        self.assertLess(areas[0], areas[1])
        self.assertLess(areas[1], areas[2])


if __name__ == '__main__':
    unittest.main()
