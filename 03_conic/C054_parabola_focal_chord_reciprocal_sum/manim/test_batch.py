import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_rotating_focal_chord(self):
        for i in range(721):
            t=.3+(math.pi-.6)*i/720
            A,B=endpoints(t); s=state(t)
            for x,y in (A,B): self.assertAlmostEqual(y*y,2*p*x)
            self.assertAlmostEqual((A[0]-p/2)*B[1]-(B[0]-p/2)*A[1],0)
            self.assertAlmostEqual(s['length'],2*p/math.sin(t)**2)
            self.assertAlmostEqual(s['reciprocal'],2/p)
            self.assertAlmostEqual(s['xproduct'],p*p/4)
            self.assertAlmostEqual(s['yproduct'],-p*p)
    def test_vertical_and_exclusion(self):
        self.assertAlmostEqual(state(math.pi/2)['length'],2*p)
        with self.assertRaises(ValueError): endpoints(0)

if __name__=="__main__": unittest.main()
