import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_affine_circle_slope_area(self):
        for i in range(301):
            s=1+i/300
            self.assertAlmostEqual(area([transform(P,s) for P in triangle]),s*area(triangle))
            A=transform((-2,-1),s);B=transform((2,1),s)
            self.assertAlmostEqual((B[1]-A[1])/(B[0]-A[0]),s*.5)
            for t in (0,.4,1.3,2.8):
                x,y=point(t,s);self.assertAlmostEqual(x*x/a**2+y*y/(s*b)**2,1)
                x,y=point(t,a/b);self.assertAlmostEqual(x*x+y*y,a*a)

if __name__=="__main__": unittest.main()
