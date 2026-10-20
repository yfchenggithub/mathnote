import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_family_focus_invariant(self):
        for kind in ('ellipse','hyperbola'):
            for i in range(101):
                t=.7+(1.3 if kind=='ellipse' else 1.)*i/100
                a,b=params(kind,t)
                self.assertAlmostEqual(a*a-b*b if kind=='ellipse' else a*a+b*b,c*c)
                for u in (.2,.8,1.1):
                    x,y=curve(kind,t,u)
                    self.assertAlmostEqual(x*x/a**2+(1 if kind=='ellipse' else -1)*y*y/b**2,1)
                    r1=math.hypot(x+c,y);r2=math.hypot(x-c,y)
                    self.assertAlmostEqual(r1+r2 if kind=='ellipse' else abs(r1-r2),2*a)

if __name__=="__main__": unittest.main()
