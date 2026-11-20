import unittest
from model import state,signed_composition
class CompositionTests(unittest.TestCase):
 def test_all_four_cases(self):
  for sg in [-1,1]:
   for sf in [-1,1]:
    self.assertEqual(signed_composition(sg,sf,3)>signed_composition(sg,sf,1),sg*sf>0)
 def test_every_animation_position(self):
  for i in range(201):
   s=state(3+i/50);a=s['blue'];b=s['orange']
   self.assertLess(a[0],b[0]);self.assertGreater(a[1],b[1]);self.assertLess(a[2],b[2])
   self.assertAlmostEqual(10-b[0],b[1]);self.assertAlmostEqual(10-b[1],b[2])
 def test_secants(self):self.assertEqual(((-1.5+.5)/(3-1))*2,-1)
 def test_boundary_conditions(self):
  for j in range(1,100):
   x=2+j/100;self.assertGreater((x-2)*(x-.5),0)
  self.assertLess(2.01**2-3*2.01+1,0)
if __name__=='__main__':unittest.main()
