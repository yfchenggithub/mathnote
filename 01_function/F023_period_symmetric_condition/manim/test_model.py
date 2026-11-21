import unittest
from model import *
class Tests(unittest.TestCase):
 def test_moving_midpoint(self):
  for k in range(-500,501):
   s=state(k/100);self.assertAlmostEqual(s["left_height"],s["right_height"]);self.assertAlmostEqual(s["right"]-s["left"],4);self.assertAlmostEqual((s["left"]+s["right"])/2,s["center"])
 def test_global_period(self):
  for k in range(-400,401):self.assertAlmostEqual(f(k/100+4),f(k/100))
 def test_one_side_not_period(self):self.assertNotAlmostEqual(f(1),f(3))
if __name__=="__main__":unittest.main()
