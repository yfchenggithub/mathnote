import unittest
from math import isclose
from model import A,B,X0,MINIMUM,state
class DistanceTests(unittest.TestCase):
 def test_intersection_and_equalities(self):
  s=state(X0);self.assertAlmostEqual(s['sum'],MINIMUM);self.assertAlmostEqual((X0-A[0])/(B[0]-A[0]),2/5)
 def test_all_positions_and_derivative(self):
  for j in range(-100,101):
   x=j/10;s=state(x);self.assertGreaterEqual(s['excess'],-1e-12)
   d=(x-1)/s['ap']+(x-3)/s['pb'];self.assertEqual(d>0,x>X0) if x!=X0 else self.assertAlmostEqual(d,0)
 def test_display_and_loop_states(self):
  for x in [5,X0,3.8,X0,5]:
   s=state(x);self.assertTrue(isclose(s['ap']**2,(x-1)**2+4));self.assertTrue(isclose(s['pb']**2,(x-3)**2+9))
if __name__=='__main__':unittest.main()
