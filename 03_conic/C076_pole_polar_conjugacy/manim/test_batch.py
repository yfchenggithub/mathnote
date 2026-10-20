import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_reciprocity(self):
        for i in range(501):
            q=Q(-1.7+3.4*i/500)
            self.assertAlmostEqual(bilinear(P,q),1)
            self.assertAlmostEqual(bilinear(q,P),1)
            self.assertGreater(q[0]*q[0]+q[1]*q[1],0)
            for r in line(q):self.assertAlmostEqual(bilinear(q,r),1)

if __name__=="__main__": unittest.main()
