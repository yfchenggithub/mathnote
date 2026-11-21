import unittest
from model import *
class Tests(unittest.TestCase):
 def test_midpoint_and_sum(self):
  for i in range(111):
   l,r=state(.4+i/100)
   self.assertAlmostEqual((l[0]+r[0])/2,CENTER[0]);self.assertAlmostEqual((l[1]+r[1])/2,CENTER[1]);self.assertAlmostEqual(l[1]+r[1],6)
 def test_center(self):self.assertEqual(f(2),3)
if __name__=="__main__":unittest.main()
