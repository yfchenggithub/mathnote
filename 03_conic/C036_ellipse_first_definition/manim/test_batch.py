import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_definition_all_states(self):
        for i in range(721):
            t=i*math.pi/360 if KIND=='ellipse' else -1.4+i*2.8/720
            for branch in (-1,1):
                x,y=point(t,branch)
                value=x*x/a**2+y*y/b**2 if KIND=='ellipse' else x*x/a**2-y*y/b**2
                self.assertAlmostEqual(value,1)
                self.assertAlmostEqual(invariant(t,branch),2*a)
        self.assertGreater(a,c) if KIND=='ellipse' else self.assertLess(a,c)

if __name__=="__main__": unittest.main()
