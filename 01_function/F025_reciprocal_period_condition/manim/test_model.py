import unittest
from model import f,state,A
class Mathematics(unittest.TestCase):
 def test_identity(self):
  for i in range(-600,601):
   x=i/37
   self.assertGreater(f(x),0)
   self.assertAlmostEqual(f(x+A)*f(x),1,places=12)
   self.assertAlmostEqual(f(x+2*A),f(x),places=12)
 def test_trajectory(self):
  for i in range(401):
   p,q,r=state(-.2+i/200)
   self.assertAlmostEqual(q[0]-p[0],A);self.assertAlmostEqual(r[0]-p[0],2*A)
   self.assertAlmostEqual(p[1]*q[1],1);self.assertAlmostEqual(r[1],p[1])
 def test_key_values(self):
  self.assertEqual(state(.5),((.5,2.0),(1.5,.5),(2.5,2.0)))
  for x in [0,1,2,3]:self.assertAlmostEqual(f(x),1,places=12)
if __name__=='__main__':unittest.main()
