from math import cos, hypot, pi, sin, tan
import unittest
from model import EDGE, UPPER, LOWER, VertexAngleModel


class VertexAngleTests(unittest.TestCase):
    def test_independent_geometry_formula_and_area(self):
        for a, b in [(2, 1), (3, 2), (4, 3.999), (5, .15)]:
            m = VertexAngleModel(a, b)
            for i in range(1, 720):
                t = i*pi/360
                if not m.admissible(t):
                    continue
                x, y = m.point(t)
                angle = m.angle(t)
                self.assertAlmostEqual(x*x/a**2+y*y/b**2, 1, places=12)
                self.assertAlmostEqual(angle, m.formula_angle(t), places=10)
                self.assertGreater(angle, pi/2)
                self.assertLessEqual(angle, m.maximum+1e-12)
                r1, r2 = hypot(x+a, y), hypot(x-a, y)
                self.assertAlmostEqual(cos(angle), (r1*r1+r2*r2-4*a*a)/(2*r1*r2), places=9)
                self.assertAlmostEqual(.5*r1*r2*sin(angle), m.area(t), places=9)
                self.assertAlmostEqual((y/(x+a))*(y/(x-a)), -b*b/(a*a), places=8)

    def test_maxima_half_angle_and_negative_tangent(self):
        m = VertexAngleModel()
        for t in (pi/2, 3*pi/2):
            self.assertAlmostEqual(m.angle(t), m.maximum, places=12)
            self.assertAlmostEqual(tan(m.angle(t)/2), m.a/m.b, places=12)
            self.assertAlmostEqual(tan(m.angle(t)), -4/3, places=12)
        self.assertAlmostEqual(m.maximum*180/pi, 126.869897645844, places=10)

    def test_endpoints_have_no_angle(self):
        m = VertexAngleModel()
        for t in (0, pi, 2*pi, -pi):
            self.assertIsNone(m.angle(t))
            self.assertIsNone(m.formula_angle(t))

    def test_endpoint_limit_is_unattained(self):
        m = VertexAngleModel()
        for base in (0, pi, 2*pi):
            for sign in (-1, 1):
                values = [m.angle(base+sign*e)-pi/2 for e in (.1, .01, .001, .0001)]
                self.assertTrue(all(v>0 for v in values))
                self.assertTrue(all(u>v for u,v in zip(values, values[1:])))
                self.assertLess(values[-1], .00008)

    def test_symmetry_and_height_monotonicity(self):
        m = VertexAngleModel()
        angles = [m.angle(EDGE+i*(pi/2-EDGE)/100) for i in range(101)]
        self.assertTrue(all(v>u for u,v in zip(angles,angles[1:])))
        for t in (.1, .5, 1, pi/2):
            for reflection in (-t, pi-t, pi+t):
                self.assertAlmostEqual(m.angle(t), m.angle(reflection), places=12)

    def test_storyboard_never_crosses_excluded_vertices(self):
        m = VertexAngleModel()
        for start, middle, end in (UPPER, LOWER):
            for i in range(401):
                t = start+(end-start)*i/400
                self.assertTrue(m.admissible(t))
                self.assertGreater(m.angle(t), pi/2)
            self.assertAlmostEqual(m.angle(middle), m.maximum, places=12)

    def test_invalid_models(self):
        for a,b in [(1,1),(1,2),(1,0),(-1,-2),(float('inf'),1)]:
            with self.assertRaises(ValueError):
                VertexAngleModel(a,b)


if __name__ == '__main__':
    unittest.main()
