import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_ratio_and_locus(self):
        for i in range(721):
            t=i*math.pi/720
            for x,y in endpoints(t):self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
            self.assertAlmostEqual(ratio(t),(1-e*math.cos(t))/(1+e*math.cos(t)))
        self.assertAlmostEqual(ratio(math.pi/2),1)

if __name__=="__main__": unittest.main()
