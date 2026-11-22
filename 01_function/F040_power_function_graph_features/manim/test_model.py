import math,unittest
from model import power,slope,category,fractional_even,example_four_inequality
class PowerModelTest(unittest.TestCase):
 def test_common_point_and_tangent(self):
  for alpha in [-4,-2,-1,-.3,0,.2,.5,1,1.7,2,math.sqrt(2)]:
   self.assertEqual(power(1,alpha),1)
   self.assertAlmostEqual(slope(1,alpha),alpha)
 def test_order_in_both_variables(self):
  for a1,a2 in [(-2,-1),(-1,0),(0,.5),(.3,.5),(.5,2)]:
   for x in [.1,.5,.8,1.2,1.7,2,4]:
    self.assertGreater((power(x,a2)-power(x,a1))*(x-1),0)
  for alpha in [-3,-1,-.5,.3,1,2]:
   for x1,x2 in [(.1,.3),(.5,.8),(1,2),(2,4)]:
    self.assertGreater((power(x2,alpha)-power(x1,alpha))*alpha,0)
 def test_five_slope_cases(self):
  for alpha in [2,1,.5,0,-1]:
   s1,s2=slope(.5,alpha),slope(2,alpha)
   if alpha>1:self.assertGreater(s2,s1);self.assertGreater(s1,0)
   elif alpha==1:self.assertEqual(s1,s2);self.assertEqual(s1,1)
   elif alpha>0:self.assertGreater(s1,s2);self.assertGreater(s2,0)
   elif alpha==0:self.assertEqual(s1,s2);self.assertEqual(s1,0)
   else:self.assertLess(s1,s2);self.assertLess(s2,0);self.assertGreater(abs(s1),abs(s2))
   self.assertTrue(category(alpha))
 def test_animation_entire_range(self):
  for i in range(601):
   alpha=-1+3*i/600
   self.assertEqual(power(1,alpha),1)
   for x in [.23,.5,1,2,2.2]:self.assertTrue(0<power(x,alpha)<5)
 def test_fractional_example_and_domain(self):
  n=2*math.sqrt(6)/9
  self.assertAlmostEqual(fractional_even(n),1.5);self.assertAlmostEqual(fractional_even(-n),1.5)
  for i in range(-100,101):
   a=i/10
   if a in [-1,3]:self.assertIsNone(example_four_inequality(a))
   else:self.assertEqual(example_four_inequality(a),a<1)
  with self.assertRaises(ValueError):power(0,0)
  with self.assertRaises(ValueError):power(-1,2/3)
if __name__=='__main__':unittest.main()
