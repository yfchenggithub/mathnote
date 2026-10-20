import unittest
from math import cos, sin, pi, sqrt
from model import EllipseLine


class TangentConditionTests(unittest.TestCase):
    def test_domain(self):
        for args in ((1, 2, 0), (2, 0, 1), (2, 2, 0), (5, 3, float('inf'))):
            with self.assertRaises(ValueError):
                EllipseLine(*args)

    def test_example_threshold(self):
        model = EllipseLine()
        self.assertAlmostEqual(model.threshold, 25)
        self.assertEqual(model.tangent_intercepts, (-5, 5))

    def test_example_contacts(self):
        self.assertEqual(EllipseLine().contact(5), (-4, 1.8))
        self.assertEqual(EllipseLine().contact(-5), (4, -1.8))

    def test_intersections_all_animation_states(self):
        model = EllipseLine()
        for i in range(1261):
            m = -6.3+i*.01
            state = model.relation(m)
            points = model.intersections(m)
            self.assertEqual(len(points), {'secant': 2, 'tangent': 1, 'disjoint': 0}[state])
            for x, y in points:
                self.assertAlmostEqual(x*x/25+y*y/9, 1, places=10)
                self.assertAlmostEqual(y, .8*x+m, places=10)

    def test_general_tangent_gradient(self):
        for a, b in ((5, 3), (3, 2), (2, .7)):
            for k in (-4, -.8, 0, .8, 4):
                model = EllipseLine(a, b, k)
                for m in model.tangent_intercepts:
                    x, y = model.contact(m)
                    self.assertAlmostEqual(x*x/a**2+y*y/b**2, 1)
                    self.assertAlmostEqual(y-k*x, m)
                    self.assertAlmostEqual(x/a**2+k*y/b**2, 0)
                    self.assertEqual(len(model.intersections(m)), 1)

    def test_discriminant_from_quadratic(self):
        for k in (-3, 0, .8, 4):
            model = EllipseLine(5, 3, k)
            for m in (-7, -5, 0, 5, 7):
                A = model.threshold
                B = 2*25*k*m
                C = 25*(m*m-9)
                self.assertAlmostEqual(B*B-4*A*C, model.discriminant(m), places=7)

    def test_near_tangent_states_not_snapped(self):
        model = EllipseLine()
        self.assertEqual(model.relation(5-1e-7), 'secant')
        self.assertEqual(model.relation(5+1e-7), 'disjoint')

    def test_horizontal_tangents(self):
        model = EllipseLine(5, 3, 0)
        self.assertEqual(model.tangent_intercepts, (-3, 3))
        self.assertEqual(model.contact(3), (0, 3))
        self.assertEqual(model.contact(-3), (0, -3))

    def test_contact_rejects_other_lines(self):
        for m in (0, 4, 6):
            with self.assertRaises(ValueError):
                EllipseLine().contact(m)

    def test_clip_animation(self):
        for k in (-2, 0, .8, 2):
            model = EllipseLine(5, 3, k)
            for i in range(127):
                m = -6.3+i*.1
                for x, y in model.clipped_line(m):
                    self.assertAlmostEqual(y, k*x+m)
                    self.assertLessEqual(abs(x), 6.2+1e-9)
                    self.assertLessEqual(abs(y), 5.3+1e-9)

    def test_tangent_parameterization_independent(self):
        for i in range(1, 60):
            t = i*pi/60
            x, y = 5*cos(t), 3*sin(t)
            k = -9*x/(25*y)
            m = y-k*x
            self.assertAlmostEqual(m*m, EllipseLine(5, 3, k).threshold)


if __name__ == '__main__':
    unittest.main()
