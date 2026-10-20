import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_direct_distances_and_linear_forms(self):
        for i in range(721):
            t=i*math.pi/360; x,y=point(t)
            self.assertAlmostEqual(x*x/9+y*y/4,1)
            self.assertAlmostEqual(radius(t,1),a+e*x)
            self.assertAlmostEqual(radius(t,2),a-e*x)
            self.assertAlmostEqual(radius(t,1)+radius(t,2),2*a)
            self.assertAlmostEqual(radius(t,1)-radius(t,2),2*e*x)

if __name__=="__main__": unittest.main()
