import unittest
from model import *
class Tests(unittest.TestCase):
 def test_reflection_and_comparison(self):
  for k in range(161):
   t=1+k/100;s=state(t)
   self.assertAlmostEqual(f(s["a"]),f(s["mirror"]))
   self.assertAlmostEqual(s["gap"],(t-1.5)*(t+1.5))
   self.assertEqual(s["gap"]>0,t>1.5)
 def test_equality(self):self.assertEqual(state(1.5)["gap"],0)
if __name__=="__main__":unittest.main()
