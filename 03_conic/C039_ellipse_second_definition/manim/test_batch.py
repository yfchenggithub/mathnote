import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_direct_distances_ratio(self):
        for i in range(721):
            t=i*math.pi/360 if KIND=='ellipse' else -1.4+2.8*i/720 if KIND=='hyperbola' else -2+4*i/720
            x,y=point(t); hx,hy=foot(t)
            self.assertEqual(hy,y); self.assertEqual(hx,directrix)
            self.assertAlmostEqual(ratio(t),e)
            if KIND=='ellipse': self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
            elif KIND=='hyperbola': self.assertAlmostEqual(x*x/a**2-y*y/b**2,1)
            else:
                self.assertAlmostEqual(y*y,2*p*x)
                self.assertAlmostEqual(distances(t)[0],x+p/2)

if __name__=="__main__": unittest.main()
