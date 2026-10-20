import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_geometric_intersections(self):
        for i in range(721):
            t=i*math.pi/360; p,q=endpoints(t)
            for x,y in (p,q):
                self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                self.assertAlmostEqual((x-c)*math.sin(t)-y*math.cos(t),0)
            self.assertAlmostEqual(length(t),2*a*b*b/(a*a*math.sin(t)**2+b*b*math.cos(t)**2))
    def test_extrema(self):
        self.assertAlmostEqual(length(0),2*a)
        self.assertAlmostEqual(length(math.pi/2),2*b*b/a)

if __name__=="__main__": unittest.main()
