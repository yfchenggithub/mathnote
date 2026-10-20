import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_distance_ratio_locus(self):
        for i in range(721):
            t=i*math.pi/360; x,y=point(t)
            self.assertAlmostEqual(ratio(t),lam)
            self.assertAlmostEqual((x-center)**2+y*y,radius*radius)
            self.assertGreater(math.hypot(x-1,y),0)

if __name__=="__main__": unittest.main()
