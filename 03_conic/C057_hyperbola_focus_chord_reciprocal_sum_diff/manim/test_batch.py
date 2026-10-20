import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_both_branch_cases(self):
        for same in (True,False):
            for i in range(201):
                t=1.15+(math.pi-2.3)*i/200 if same else -.2+.4*i/200
                A,B=endpoints(t)
                self.assertEqual(A[0]*B[0]>0,same)
                for x,y in (A,B):self.assertAlmostEqual(x*x/a**2-y*y/b**2,1)
                self.assertAlmostEqual(reciprocal(t),2*a/b**2)
    def test_asymptote_excluded(self):
        with self.assertRaises(ValueError):endpoints(math.atan(b/a))

if __name__=="__main__": unittest.main()
