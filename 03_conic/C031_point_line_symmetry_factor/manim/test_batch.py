import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_reflection_geometry(self):
        for i in range(361):
            t=i*math.pi/180; p,q,h=point(t),reflected(t),foot(t)
            self.assertAlmostEqual(A*h[0]+B*h[1]+C,0)
            self.assertAlmostEqual((q[0]-p[0])*B-(q[1]-p[1])*A,0)
            self.assertAlmostEqual(math.dist(p,h),math.dist(q,h))
            factor=(A*q[0]+B*q[1]+C)/(A*A+B*B)
            self.assertAlmostEqual(q[0]-2*A*factor,p[0])
            self.assertAlmostEqual(q[1]-2*B*factor,p[1])

if __name__=="__main__": unittest.main()
