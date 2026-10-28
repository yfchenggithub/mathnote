import unittest
from math import sqrt
from model import radii, snapshot, residuals


class C086ModelTests(unittest.TestCase):
    def test_three_key_states(self):
        self.assertEqual(snapshot(1, 2, 2)['points'], [(1.5, sqrt(15)/2), (1.5, -sqrt(15)/2)])
        self.assertEqual(snapshot(1, 3, 2)['points'], [(1, 0)])
        self.assertEqual(snapshot(1, 3.5, 2)['points'], [])

    def test_existence_and_geometry_across_ratios(self):
        for a in [.5, 1, 2, 5]:
            for ratio in [.1, .3, .5, .9, 1.1, 2, 3, 10]:
                upper = (1+ratio)/abs(1-ratio)
                for e in [1+(upper-1)*.1, (1+upper)/2, upper, upper+.4]:
                    s = snapshot(a, a*e, ratio)
                    expected = 0 if e > upper+1e-10 else (1 if abs(e-upper)<1e-10 else 2)
                    self.assertEqual(s['count'], expected)
                    for row in residuals(s):
                        self.assertLess(max(row), 2e-9)
                    if s['count'] == 1:
                        self.assertAlmostEqual(s['points'][0][0], a if ratio > 1 else -a)

    def test_animation_sweep(self):
        for i in range(1501):
            s = snapshot(1, 2+1.5*i/1500, 2)
            for row in residuals(s):
                self.assertLess(max(row), 1e-11)
            self.assertEqual(s['count'], 2 if i < 1000 else (1 if i == 1000 else 0))

    def test_reciprocal_reflection(self):
        for ratio in [2, 3, 5]:
            upper = (ratio+1)/(ratio-1)
            for e in [(1+upper)/2, upper]:
                p = snapshot(1, e, ratio)['points']
                q = snapshot(1, e, 1/ratio)['points']
                for (x, y), (u, v) in zip(p, q):
                    self.assertAlmostEqual(x, -u)
                    self.assertAlmostEqual(y, v)

    def test_invalid_and_equal_ratio(self):
        for args in [(0,2), (1,1), (1,0), (1,-2)]:
            with self.assertRaises(ValueError):
                radii(*args)
        with self.assertRaises(ValueError):
            snapshot(1, 1, 2)


if __name__ == '__main__':
    unittest.main()
