import unittest
from fractions import Fraction as Q
from model_infinity import *
class InfinityModelTests(unittest.TestCase):
 def test_exact_identities(self):
  for k in range(40,801):
   x=Q(k,10)
   self.assertEqual(ratio(x),2+ratio_error(x))
   self.assertEqual(derivative_ratio(x),2+Q(3,2)/x)
   self.assertGreater(denominator_prime(x),0)
   self.assertGreater(ratio(x),derivative_ratio(x))
   self.assertGreater(derivative_ratio(x),2)
   self.assertLess(ratio_error(x),3/x)
 def test_derivatives(self):
  for k in range(4,81):
   x=Q(k);h=Q(1,100)
   self.assertEqual((numerator(x+h)-numerator(x-h))/(2*h),numerator_prime(x))
   self.assertEqual((denominator(x+h)-denominator(x-h))/(2*h),denominator_prime(x))
 def test_growth_and_convergence(self):
  for x in [4,10,20,40,80,1000,1000000]:
   self.assertGreaterEqual(numerator(x),2*x*x)
   self.assertGreaterEqual(denominator(x),x*x)
  self.assertLess(ratio_error(1000000),.000003)
  self.assertLess(derivative_error(1000000),.000002)
 def test_key_states(self):
  self.assertAlmostEqual(ratio(10),231/101)
  self.assertAlmostEqual(ratio(80),13041/6401)
  self.assertEqual(derivative_ratio(80),2.01875)
if __name__=='__main__':unittest.main()
