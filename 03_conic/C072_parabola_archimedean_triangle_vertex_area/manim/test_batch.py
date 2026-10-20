import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_tangents_midpoint_area(self):
        for i in range(501):
            t=-.45+.9*i/500;d=.8+.5*i/500
            A,B,P,M=state(t,d)
            for x,y in (A,B):
                self.assertAlmostEqual(x*x,2*p*y)
                self.assertAlmostEqual(x*P[0],p*(P[1]+y))
            self.assertAlmostEqual(P[0],M[0])
            self.assertAlmostEqual(area(t,d),abs(A[0]-B[0])**3/(8*p))

if __name__=="__main__": unittest.main()
