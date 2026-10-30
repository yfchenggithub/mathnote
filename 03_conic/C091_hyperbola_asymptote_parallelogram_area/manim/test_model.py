import unittest
from model import from_point, on_hyperbola


class C091GeometryTests(unittest.TestCase):
    def test_curve_incidence_parallelism_and_area(self):
        for a, b in [(3, 2), (2, 3), (2, 2), (.5, 4)]:
            for branch in (-1, 1):
                for i in range(101):
                    s = on_hyperbola(-1.5 + 3*i/100, a, b, branch)
                    x, y = s.p
                    self.assertAlmostEqual(x*x/a**2-y*y/b**2, 1)
                    self.assertAlmostEqual(s.q[1], b*s.q[0]/a)
                    self.assertAlmostEqual(s.r[1], -b*s.r[0]/a)
                    self.assertAlmostEqual(s.q[0]+s.r[0], x)
                    self.assertAlmostEqual(s.q[1]+s.r[1], y)
                    self.assertAlmostEqual(y-s.q[1], -b*(x-s.q[0])/a)
                    self.assertAlmostEqual(y-s.r[1], b*(x-s.r[0])/a)
                    self.assertAlmostEqual(s.area, a*b/2)

    def test_formal_example(self):
        s = from_point(13/4, 5/6)
        self.assertEqual(s.q, (9/4, 3/2))
        self.assertAlmostEqual(s.r[0], 1)
        self.assertAlmostEqual(s.r[1], -2/3)
        self.assertAlmostEqual(s.area, 3)

    def test_vertex_and_general_point_formula(self):
        self.assertEqual(on_hyperbola(0).p, (3, 0))
        for x, y in [(0, 0), (3, 2), (-3, 2), (0, 2), (4, -1)]:
            s = from_point(x, y)
            self.assertAlmostEqual(s.area, 3*abs(x*x/9-y*y/4))
        self.assertAlmostEqual(from_point(3, 2).area, 0)
        self.assertAlmostEqual(from_point(0, 2).area, 3)

    def test_invalid_conditions(self):
        for a,b in [(0,2),(3,0),(-3,2)]:
            with self.assertRaises(ValueError):
                from_point(3,0,a,b)
        with self.assertRaises(ValueError):
            on_hyperbola(0,branch=0)


if __name__ == '__main__':
    unittest.main()
