import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_actual_contacts_and_tangency(self):
        for i in range(721):
            t=.35+2*math.pi*i/720 if KIND in ('ellipse','monge') else 1.3+1.3*i/720 if KIND=='hyperbola' else -.8+1.6*i/720
            P,A,B=state(t)
            for x,y in (A,B):
                if KIND in ('ellipse','monge'):
                    self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                    self.assertAlmostEqual(x*(P[0]-x)/a**2+y*(P[1]-y)/b**2,0)
                elif KIND=='hyperbola':
                    self.assertAlmostEqual(x*x/a**2-y*y/b**2,1)
                    self.assertAlmostEqual(x*(P[0]-x)/a**2-y*(P[1]-y)/b**2,0)
                else:
                    self.assertAlmostEqual(y*y,2*p*x)
                    self.assertAlmostEqual(-p*(P[0]-x)+y*(P[1]-y),0)
                self.assertAlmostEqual(polar(P,(x,y)),0)
            if KIND=='monge':
                self.assertAlmostEqual((A[0]-P[0])*(B[0]-P[0])+(A[1]-P[1])*(B[1]-P[1]),0)
                self.assertAlmostEqual(P[0]**2+P[1]**2,a*a+b*b)
                self.assertAlmostEqual(angle(t),90)

if __name__=="__main__": unittest.main()
