import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_two_endpoint_slopes(self):
        for i in range(501):
            t=.2+(math.pi-.4)*i/500 if KIND=='ellipse' else .2+1.1*i/500
            x,y=point(t);k,l=slopes(t)
            self.assertAlmostEqual(k*(x+a),y);self.assertAlmostEqual(l*(x-a),y)
            self.assertAlmostEqual(product(t),(-1 if KIND=='ellipse' else 1)*b*b/(a*a))
        with self.assertRaises(ValueError):slopes(0)

if __name__=="__main__": unittest.main()
