import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_tangent_point_and_direction(self):
        for i in range(501):
            t=-1.1+2.2*i/500 if KIND=='hyperbola' else -2+4*i/500
            x,y=point(t);A,B,C=tangent(t)
            self.assertAlmostEqual(A*x+B*y,C)
            for qx,qy in segment(t):self.assertAlmostEqual(A*qx+B*qy,C)
            dx,dy=(a*math.sinh(t),b*math.cosh(t)) if KIND=='hyperbola' else (t/p,1)
            self.assertAlmostEqual(A*dx+B*dy,0)

if __name__=="__main__": unittest.main()
