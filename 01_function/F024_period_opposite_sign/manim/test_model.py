import unittest
from model import f,state,A
class Mathematics(unittest.TestCase):
 def test_continuous_identity(self):
  for i in range(-600,601):
   x=i/37
   self.assertAlmostEqual(f(x+A),-f(x),places=12)
   self.assertAlmostEqual(f(x+2*A),f(x),places=12)
 def test_geometry(self):
  for i in range(301):
   p,q,r=state(-.4+i/100)
   self.assertAlmostEqual(q[0]-p[0],A);self.assertAlmostEqual(r[0]-q[0],A)
   self.assertAlmostEqual(q[1],-p[1]);self.assertAlmostEqual(r[1],p[1])
 def test_key_states(self):
  self.assertEqual(state(1),((1,1.0),(3,-1.0),(5,1.0)))
  for x in [0,2,4]:self.assertAlmostEqual(f(x),0,places=12)
if __name__=='__main__':unittest.main()
