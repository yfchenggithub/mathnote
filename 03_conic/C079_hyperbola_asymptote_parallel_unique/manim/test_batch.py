import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_one_transverse_intersection(self):
        for i in range(501):
            for sign in (-1,1):
                m=sign*(.8+.8*i/500);x,y=point(m)
                self.assertAlmostEqual(x*x/a**2-y*y/b**2,1)
                self.assertAlmostEqual(y,k*x+m)
                # Directional derivative along the line is nonzero: this is not tangency.
                self.assertAlmostEqual(2*x/a**2-2*y*k/b**2,-2*m/(a*b))
        with self.assertRaises(ValueError):point(0)

if __name__=="__main__": unittest.main()
