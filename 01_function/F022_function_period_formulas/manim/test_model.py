import unittest
from model import *
class Tests(unittest.TestCase):
 def test_real_function(self):
  for k in range(-701,702):
   x=k/100
   self.assertEqual(f(x+1),phi(f(x)));self.assertEqual(f(x+2),f(x));self.assertNotEqual(f(x+1),f(x))
 def test_jump_endpoints(self):
  self.assertEqual(f(1-1e-8),2);self.assertEqual(f(1),3);self.assertEqual(f(2-1e-8),3);self.assertEqual(f(2),2)
 def test_denominator(self):
  for u in [-5,-2,-.5,0,.5,1.5,2,3,7]:self.assertAlmostEqual(phi(phi(u)),u)
if __name__=="__main__":unittest.main()
