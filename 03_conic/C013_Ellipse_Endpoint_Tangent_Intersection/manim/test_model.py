import math
import unittest
from model import state, shoelace


class ModelTests(unittest.TestCase):
    def test_tangency_and_intersections(self):
        for a,b in ((2,1),(3,2),(4,2)):
            for side in (-1,1):
                for i in range(-50,51):
                    s=state(i/20,a,b,side); x,y=s['p']; k,m=s['k'],s['m']
                    self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                    self.assertAlmostEqual(y,k*x+m)
                    self.assertAlmostEqual(m*m-a*a*k*k,b*b)
                    for xx,yy in (s['p1'],s['p2']):
                        self.assertAlmostEqual(yy,k*xx+m)
                        self.assertAlmostEqual(x*xx/a**2+y*yy/b**2,1)
                    self.assertGreater(side*y,0)

    def test_invariant_and_same_side(self):
        for side in (-1,1):
            for i in range(-100,101):
                s=state(i/25,side=side)
                self.assertAlmostEqual(s['d1']*s['d2'],1)
                self.assertGreater(side*s['p1'][1],0)
                self.assertGreater(side*s['p2'][1],0)

    def test_area_independent_polygon(self):
        for side in (-1,1):
            for u in (-2,-.8,0,.8,2):
                s=state(u,side=side)
                self.assertAlmostEqual(shoelace([s['a1'],s['p1'],s['p2'],s['a2']]),s['area'])
                self.assertAlmostEqual(s['area'],4/abs(s['p'][1]))
                self.assertGreaterEqual(s['area'],4)

    def test_minimum_and_endpoint_exclusion(self):
        for side in (-1,1):
            s=state(0,side=side)
            self.assertEqual(s['p'],(0,side))
            self.assertEqual(s['area'],4)
            self.assertEqual(s['d1'],s['d2'])
            previous=4
            for u in (.2,.8,2,5,8):
                s=state(u,side=side)
                self.assertGreater(s['area'],previous)
                self.assertGreater(abs(s['p'][1]),0)
                self.assertLess(s['p'][0],2)
                previous=s['area']

    def test_displayed_states(self):
        for u in (-.8,.8):
            s=state(u)
            self.assertAlmostEqual(s['area'],4*math.cosh(.8))
            self.assertAlmostEqual(max(s['d1'],s['d2']),math.exp(.8))
        s=state(math.log(2),4,2)
        self.assertAlmostEqual(s['d1'],4)
        self.assertAlmostEqual(s['d2'],1)
        self.assertAlmostEqual(s['area'],20)

    def test_domain(self):
        for a,b,side in ((1,1,1),(1,2,1),(2,0,1),(2,1,0)):
            with self.assertRaises(ValueError): state(.5,a,b,side)


if __name__=='__main__': unittest.main()
