import math
import unittest
from model import point, tangent, slopes, product, clip_line


class ModelTests(unittest.TestCase):
    def test_ellipse_and_tangency(self):
        for a,b in ((2,1),(3,2),(5,4)):
            for i in range(361):
                t = i*math.pi/180
                x,y=point(t,a,b)
                A,B,C=tangent(t,a,b)
                self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                self.assertAlmostEqual(A*x+B*y,C)
                self.assertAlmostEqual(A*(-a*math.sin(t))+B*b*math.cos(t),0)

    def test_invariant_all_quadrants(self):
        for a,b in ((2,1),(3,2),(5,4)):
            for i in range(720):
                t=(i+.5)*math.pi/360
                self.assertAlmostEqual(product(t,a,b),-b*b/a**2)
                self.assertAlmostEqual(product(t,a,b),(1-b*b/a**2)-1)

    def test_axis_exceptions(self):
        for i in range(4):
            t=i*math.pi/2
            r,s=slopes(t)
            self.assertIsNone(product(t))
            self.assertEqual((r is None,s is None),(i%2==1,i%2==0))
            self.assertAlmostEqual(s if i%2 else r,0)

    def test_numeric_states(self):
        r,s=slopes(math.pi/4)
        self.assertAlmostEqual(r,.5)
        self.assertAlmostEqual(s,-.5)
        self.assertAlmostEqual(product(math.atan(2)),-.25)
        r,s=slopes(math.atan(2))
        self.assertAlmostEqual(r,1)
        self.assertAlmostEqual(s,-.25)
        r,s=slopes(math.atan(4/3),3,2)
        self.assertAlmostEqual(r,8/9)
        self.assertAlmostEqual(s,-.5)

    def test_general_line_clipping(self):
        for i in range(361):
            abc=tangent(i*math.pi/180)
            for x,y in clip_line(*abc):
                self.assertAlmostEqual(abc[0]*x+abc[1]*y,abc[2])
                self.assertLessEqual(abs(x),2.6+1e-9)
                self.assertLessEqual(abs(y),2.1+1e-9)

    def test_nonperpendicular_and_domain(self):
        for t in (.2,.5,1.,2.,4.,5.):
            self.assertNotAlmostEqual(product(t),-1)
        for a,b in ((1,1),(1,2),(2,0)):
            with self.assertRaises(ValueError):
                point(.5,a,b)


if __name__=='__main__':
    unittest.main()
