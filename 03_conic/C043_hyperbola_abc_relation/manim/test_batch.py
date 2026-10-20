import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_right_triangle_and_parameter_identity(self):
        for i in range(101):
            bb=.9+1.4*i/100; a,b,c=parameters(bb); pts=triangle(bb)
            if KIND=='ellipse':
                self.assertAlmostEqual(math.dist(pts[1],pts[2]),a)
                self.assertAlmostEqual(a*a,b*b+c*c)
            else:
                self.assertAlmostEqual(math.dist(pts[0],pts[2]),c)
                self.assertAlmostEqual(c*c,a*a+b*b)

if __name__=="__main__": unittest.main()
