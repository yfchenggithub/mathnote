import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_focus_chord_endpoints(self):
        for kind in ('ellipse','hyperbola','parabola'):
            for i in range(201):
                t=(1+i/200) if kind=='ellipse' else (.8+.7*i/200) if kind=='hyperbola' else (1+.8*i/200)
                a,b,c=params(kind,t);A,B=endpoints(kind,t)
                self.assertEqual(A[0],B[0]);self.assertAlmostEqual(A[0],c)
                for x,y in (A,B):
                    if kind=='ellipse':self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                    elif kind=='hyperbola':self.assertAlmostEqual(x*x/a**2-y*y/b**2,1)
                    else:self.assertAlmostEqual(y*y,2*t*x)
                self.assertAlmostEqual(A[1]-B[1],2*t if kind=='parabola' else 2*b*b/a)

if __name__=="__main__": unittest.main()
