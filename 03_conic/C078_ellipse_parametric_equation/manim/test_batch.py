import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_circle_projection(self):
        for i in range(721):
            Q,P=state(i*math.pi/360)
            self.assertAlmostEqual(Q[0]**2+Q[1]**2,a*a)
            self.assertAlmostEqual(P[0]**2/a**2+P[1]**2/b**2,1)
            self.assertAlmostEqual(Q[0],P[0]);self.assertAlmostEqual(P[1],b/a*Q[1])

if __name__=="__main__": unittest.main()
