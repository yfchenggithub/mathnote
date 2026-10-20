import math
import unittest
from model import state, clip_line


class ModelTests(unittest.TestCase):
    def test_point_and_tangent(self):
        for a,b in ((3,2),(2,1),(5,3)):
            for i in range(361):
                t=i*math.pi/180
                s=state(t,a,b)
                x,y=s['p']; A,B,C=s['line']
                self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                self.assertAlmostEqual(A*x+B*y,C)
                self.assertAlmostEqual(A*(-a*math.sin(t))+B*b*math.cos(t),0)

    def test_foot_and_distance(self):
        for i in range(721):
            s=state(i*math.pi/360)
            A,B,C=s['line']; hx,hy=s['h']; px,py=s['p']
            self.assertAlmostEqual(A*hx+B*hy,C)
            self.assertAlmostEqual(hx*(px-hx)+hy*(py-hy),0)
            self.assertAlmostEqual(math.hypot(hx,hy),s['d'])
            self.assertLessEqual(s['d'],math.hypot(px,py)+1e-10)

    def test_focal_and_product_identities(self):
        for a,b in ((3,2),(2,1),(5,3)):
            c=math.sqrt(a*a-b*b)
            for i in range(721):
                t=i*math.pi/360; s=state(t,a,b); x,y=s['p']
                self.assertAlmostEqual(s['r1'],a+c*x/a)
                self.assertAlmostEqual(s['r2'],a-c*x/a)
                self.assertAlmostEqual(s['r1']+s['r2'],2*a)
                self.assertAlmostEqual(s['g']**2,a*a-(c*x/a)**2)
                self.assertAlmostEqual(s['d']*s['g'],a*b)
                self.assertGreaterEqual(s['d']+1e-10,b)
                self.assertLessEqual(s['d'],a+1e-10)

    def test_axis_extrema(self):
        for i in range(4):
            s=state(i*math.pi/2)
            self.assertAlmostEqual(s['d'],2 if i%2 else 3)
            self.assertAlmostEqual(s['g'],3 if i%2 else 2)
            for p,h in zip(s['p'],s['h']): self.assertAlmostEqual(p,h)

    def test_numeric_and_not_OP(self):
        s=state(math.pi/4)
        self.assertAlmostEqual(s['g'],math.sqrt(6.5))
        self.assertAlmostEqual(s['d'],6/math.sqrt(6.5))
        self.assertLess(s['d'],math.hypot(*s['p']))
        t=math.acos(math.sqrt(2/3))
        s=state(t,2,1)
        self.assertAlmostEqual(s['g']**2,2)
        self.assertAlmostEqual(s['d'],math.sqrt(2))

    def test_clipping_and_domain(self):
        for i in range(361):
            s=state(i*math.pi/180)
            A,B,C=s['line']
            for x,y in clip_line(A,B,C):
                self.assertAlmostEqual(A*x+B*y,C)
                self.assertLessEqual(abs(x),3.55+1e-9)
                self.assertLessEqual(abs(y),3+1e-9)
        for a,b in ((1,1),(1,2),(2,0)):
            with self.assertRaises(ValueError): state(.5,a,b)


if __name__=='__main__': unittest.main()
