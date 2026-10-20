import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_all_stationary_candidates_and_global_comparison(self):
        self.assertGreater(M[0]**2/a**2+M[1]**2/b**2,1)
        self.assertEqual(len(roots),2) # This concrete off-axis external point has two simple stationary points.
        for t in roots:
            x,y=point(t);dx,dy=-a*math.sin(t),b*math.cos(t)
            self.assertAlmostEqual(derivative(t),0,places=10)
            self.assertAlmostEqual((x-M[0])*dx+(y-M[1])*dy,0,places=10)
        low,high=distance(tmin),distance(tmax)
        for i in range(20001):
            t=2*math.pi*i/20000
            self.assertGreaterEqual(distance(t)+1e-9,low)
            self.assertLessEqual(distance(t)-1e-9,high)
        self.assertLess(abs((distance(tmin+1e-4)-distance(tmin-1e-4))/(2e-4)),1e-6)

if __name__=="__main__": unittest.main()
