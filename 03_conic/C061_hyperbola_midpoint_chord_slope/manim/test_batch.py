import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_midpoint_and_slope(self):
        for i in range(501):
            t=.55+(math.pi-1.1)*i/500 if KIND=='ellipse' else -.7+1.4*i/500 if KIND=='hyperbola' else .7+.8*i/500
            A,B=endpoints(t); x,y=midpoint(t)
            for qx,qy in (A,B):
                if KIND=='ellipse':self.assertAlmostEqual(qx*qx/a**2+qy*qy/b**2,1)
                elif KIND=='hyperbola':self.assertAlmostEqual(qx*qx/a**2-qy*qy/b**2,1)
                else:self.assertAlmostEqual(qy*qy,2*p*qx)
            expected=-b*b*x/(a*a*y) if KIND=='ellipse' else b*b*x/(a*a*y) if KIND=='hyperbola' else p/y
            self.assertAlmostEqual(slope(t),expected)
            if KIND=='ellipse':self.assertLess(x*x/a**2+y*y/b**2,1)
            elif KIND=='hyperbola':self.assertLess(x*x/a**2-y*y/b**2,1)

if __name__=="__main__": unittest.main()
