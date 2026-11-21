import unittest
from model import *
class Tests(unittest.TestCase):
 def test_all_pairs(self):
  for k in range(151):
   t=.4+k/100;s=state(t);self.assertAlmostEqual((s["left"]+s["right"])/2,AXIS);self.assertAlmostEqual(f(s["left"]),s["height"]);self.assertAlmostEqual(f(s["right"]),s["height"])
 def test_reflection_is_involution(self):
  for x in [-3,0,1,2,4,9]:self.assertEqual(2*AXIS-(2*AXIS-x),x)
if __name__=="__main__":unittest.main()
