import unittest
from model import *
class ModelTests(unittest.TestCase):
 def test_boundary(self):
  for c in [-2,-1,0,1,2]:self.assertEqual(globally_strict_increasing(c),c>=0)
 def test_all_sample_pairs(self):
  xs=[i/10 for i in range(-30,31)]
  for c in [0,.1,1,2]:
   for x,y in zip(xs,xs[1:]):self.assertLess(value(x,c),value(y,c))
 def test_counterexample(self):
  for c in [-100,-2,-.01,-1e-8]:
   v=witness(c);self.assertGreater(v,0);self.assertLess(value(v,c),value(0,c))
 def test_point_ownership(self):
  self.assertEqual(value(0,2),0);self.assertAlmostEqual(value(1e-8,2),2+1e-8)
if __name__=='__main__':unittest.main()
