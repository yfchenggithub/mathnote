import unittest
from model import A, B, O, KINDS, area, construct, determinant, moving_b_y, triangle_area


class GeometryTests(unittest.TestCase):
    def test_four_constructions(self):
        expected = ((2, 4/3), (4.5, 3), (3, 4.5), (4/3, 2))
        for kind, hit in zip(KINDS, expected):
            c = construct(kind)
            for actual, wanted in zip(c.intersection, hit):
                self.assertAlmostEqual(actual, wanted)
            self.assertAlmostEqual(c.computed_area, 2.5)
            self.assertAlmostEqual(determinant(c.other, c.intersection), 0)
            s0, s1 = c.partial_areas
            self.assertAlmostEqual(s0+s1 if c.internal else abs(s0-s1), 2.5)

    def test_all_signs_and_zero_denominators(self):
        for x1 in range(-3, 4):
            for y1 in range(-3, 4):
                for x2 in range(-3, 4):
                    for y2 in range(-3, 4):
                        a, b = (x1, y1), (x2, y2)
                        for kind in KINDS:
                            c = construct(kind, a, b)
                            if c is not None:
                                self.assertAlmostEqual(c.computed_area, area(a, b))
                                s0, s1 = c.partial_areas
                                self.assertAlmostEqual(s0+s1 if c.internal else abs(s0-s1), area(a,b))
                            else:
                                other, start = (a, b) if kind.startswith('B') else (b, a)
                                i = 0 if kind.endswith('vertical') else 1
                                self.assertEqual(other[i], 0)
                                self.assertAlmostEqual(abs(other[1-i]*start[i])/2, area(a,b))

    def test_motion_matches_display(self):
        for segment in range(3):
            for i in range(201):
                y = moving_b_y(segment, i/200)
                b = (2, y)
                self.assertAlmostEqual(area(A,b), abs(3*y-4)/2)
                self.assertAlmostEqual(triangle_area(O,A,b), area(A,b))
        self.assertAlmostEqual(area(A,(2,4/3)), 0)
        self.assertLess(determinant(A,(2,.5)), 0)
        self.assertGreater(determinant(A,B), 0)

    def test_swap_and_collinear(self):
        self.assertEqual(area(A,B), area(B,A))
        self.assertEqual(determinant(A,B), -determinant(B,A))
        self.assertEqual(area(A,(6,4)), 0)
        self.assertEqual(area(O,B), 0)


if __name__ == '__main__':
    unittest.main()
