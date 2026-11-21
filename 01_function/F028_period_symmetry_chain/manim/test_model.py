import unittest
from model import f,pair,is_axis
class Model(unittest.TestCase):
 def test_half_period_axes(self):
  for k in range(-5,6):
   for j in range(71):
    t=j/31;p,q=pair(k,t);self.assertAlmostEqual(p[1],q[1]);self.assertTrue(is_axis(k))
 def test_candidate_not_axis(self):
  for a in [.25,.5,.75,1.25,1.5,1.75]:
   p,q=pair(a,.4);self.assertGreater(abs(p[1]-q[1]),.1);self.assertFalse(is_axis(a))
 def test_period_not_half(self):self.assertAlmostEqual(f(0),f(2));self.assertNotAlmostEqual(f(0),f(1))
if __name__=='__main__':unittest.main()
