import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_geometry_and_formula(self):
        for i in range(501):
            t=.15+(math.pi-.3)*i/500 if KIND=='ellipse' else .15+1.1*i/500
            x,y=point(t); s=state(t)
            self.assertAlmostEqual(s['r1'],abs(a+e*x))
            self.assertAlmostEqual(s['r2'],abs(a-e*x))
            if KIND=='ellipse': self.assertAlmostEqual(s['area'],b*b*math.tan(s['angle']/2))
            else: self.assertAlmostEqual(s['area'],b*b/math.tan(s['angle']/2))
            cross=abs((-c-x)*(-y)-(c-x)*(-y))/2
            self.assertAlmostEqual(s['area'],cross)

if __name__=="__main__": unittest.main()
