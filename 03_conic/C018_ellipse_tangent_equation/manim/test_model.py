import unittest
from math import pi, sin, cos, hypot, sqrt
from model import Ellipse


class TangentEquationTests(unittest.TestCase):
    def test_domain(self):
        for a, b in ((1, 2), (2, 2), (2, 0), (float('inf'), 2)):
            with self.assertRaises(ValueError):
                Ellipse(a, b)

    def test_formal_example(self):
        x, y = Ellipse().point(pi/3)
        self.assertAlmostEqual(x, 1.5)
        self.assertAlmostEqual(y, sqrt(3))
        self.assertAlmostEqual(x*x/9+y*y/4, 1)

    def test_curve_and_tangent_through_point(self):
        for a, b in ((3, 2), (5, 3), (2, .7)):
            model = Ellipse(a, b)
            for i in range(721):
                t = i*pi/360
                x, y = model.point(t)
                A, B, C = model.tangent(t)
                self.assertAlmostEqual(x*x/a**2+y*y/b**2, 1)
                self.assertAlmostEqual(A*x+B*y, C)
                self.assertAlmostEqual(A*(-a*sin(t))+B*(b*cos(t)), 0)

    def test_support_and_unique_contact(self):
        model = Ellipse()
        for i in range(60):
            t = i*pi/30
            for j in range(60):
                s = j*pi/30
                value = model.support_value(t, s)
                self.assertLessEqual(value, 1+1e-12)
                self.assertAlmostEqual(value, cos(t-s))
                if i != j:
                    self.assertLess(value, 1-1e-6)

    def test_chord_contains_both_points(self):
        model = Ellipse()
        for i in range(101):
            t, s = pi/3, i*pi/300
            A, B, C = model.chord(t, s)
            for x, y in (model.point(t), model.point(s)):
                self.assertAlmostEqual(A*x+B*y, C)

    def test_chord_limit(self):
        model = Ellipse()
        for t in (0, pi/3, pi/2, pi, 3*pi/2):
            exact = model.tangent(t)
            for v, w in zip(model.chord(t, t), exact):
                self.assertAlmostEqual(v, w)
            near = model.chord(t, t-1e-7)
            self.assertLess(max(abs(v-w) for v, w in zip(near, exact)), 1e-7)

    def test_four_vertices(self):
        model = Ellipse()
        for t, expected in ((0, (1/3, 0, 1)), (pi/2, (0, .5, 1)), (pi, (-1/3, 0, 1)), (3*pi/2, (0, -.5, 1))):
            for v, w in zip(model.tangent(t), expected):
                self.assertAlmostEqual(v, w)

    def test_clip_all_render_angles(self):
        model = Ellipse()
        for i in range(1441):
            t = i*pi/720
            A, B, C = line = model.tangent(t)
            ends = model.clipped(line)
            self.assertEqual(len(ends), 2)
            for x, y in ends:
                self.assertAlmostEqual(A*x+B*y, C)
                self.assertLessEqual(abs(x), 3.75+1e-9)
                self.assertLessEqual(abs(y), 3.1+1e-9)

    def test_vertical_horizontal_nearby_clip(self):
        model = Ellipse()
        for t in (0, 1e-10, pi/2-1e-10, pi/2, pi, 3*pi/2):
            A, B, C = line = model.tangent(t)
            for x, y in model.clipped(line):
                self.assertAlmostEqual(A*x+B*y, C)

    def test_normal_usually_not_radius(self):
        x, y = Ellipse().point(pi/3)
        A, B, _ = Ellipse().tangent(pi/3)
        self.assertGreater(abs(x*B-y*A), .1)

    def test_line_condition_crosscheck(self):
        model = Ellipse()
        for i in range(361):
            A, B, C = model.tangent(i*pi/180)
            self.assertAlmostEqual(C*C, 9*A*A+4*B*B)


if __name__ == '__main__':
    unittest.main()
