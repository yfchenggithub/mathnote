import unittest
from math import sqrt
from model import P,Q,secants,second_point,intercept,M_MIN,M_MAX

class C095Tests(unittest.TestCase):
    def test_formal_example(self):
        m,n=secants(2)
        for a,b in zip(m,(10/7,-1/7)): self.assertAlmostEqual(a,b)
        for a,b in zip(n,(26/7,-17/7)): self.assertAlmostEqual(a,b)
        self.assertAlmostEqual(intercept(2),9/7)
    def test_all_motion_states(self):
        for i in range(1001):
            k=M_MIN+(M_MAX-M_MIN)*i/1000
            m,n=secants(k)
            for point,slope in [(m,k),(n,-k)]:
                x,y=point
                self.assertAlmostEqual(x*x/2-y*y,1,places=10)
                self.assertAlmostEqual((y-1)/(x-2),slope,places=10)
                self.assertGreater(abs(x-2),.3)
                self.assertAlmostEqual(x+y,intercept(k),places=10)
                self.assertTrue(0<x<7 and -4.8<y<1.7)
            dx=m[0]-n[0];dy=m[1]-n[1]
            self.assertAlmostEqual(dx+dy,0,places=10)
            self.assertAlmostEqual(dy/dx,-1,places=10)
            self.assertLess(m[0],2);self.assertGreater(n[0],2)
            self.assertGreater(intercept(k),1)
    def test_boundaries_rejected(self):
        for k in [1,1/sqrt(2),-1/sqrt(2)]:
            with self.assertRaises(ValueError): second_point(k)
        with self.assertRaises(ValueError):secants(0)
        with self.assertRaises(ValueError):secants(-1)
    def test_fixed_tangent(self):
        self.assertEqual(P,(2,1)); self.assertEqual(Q,(2,-1))
        self.assertEqual(Q[0]**2/2-Q[1]**2,1)
        self.assertEqual(sum(Q),1)
        # Substitution of y=1-x gives (x-2)^2=0: tangent at Q.
        for x in [-2,0,1,2,3,6]:
            self.assertAlmostEqual(x*x/2-(1-x)**2-1,-.5*(x-2)**2)

if __name__=='__main__':unittest.main()
