import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_bisectors_and_reflection(self):
        for kind in ('ellipse','hyperbola','parabola'):
            for i in range(301):
                t=.6+1.9*i/300 if kind=='ellipse' else .4+.7*i/300 if kind=='hyperbola' else .5+1.3*i/300
                P,F,G,u,v,w,n=state(kind,t);aa,bb=angles(kind,t)
                self.assertAlmostEqual(aa,bb)
                if kind=='hyperbola':self.assertAlmostEqual(w[0]*n[0]+w[1]*n[1],0)
                else:self.assertAlmostEqual(abs(w[0]*n[0]+w[1]*n[1]),1)
                # Reflect a direction at the tangent using its true normal.
                incoming=(-u[0],-u[1]);dot=incoming[0]*n[0]+incoming[1]*n[1]
                reflected=(incoming[0]-2*dot*n[0],incoming[1]-2*dot*n[1])
                desired=v if kind!='hyperbola' else (-v[0],-v[1])
                self.assertAlmostEqual(reflected[0],desired[0]);self.assertAlmostEqual(reflected[1],desired[1])

if __name__=="__main__": unittest.main()
