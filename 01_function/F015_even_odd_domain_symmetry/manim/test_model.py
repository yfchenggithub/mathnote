import unittest
from model import *
class SymmetryTests(unittest.TestCase):
 def test_animation_states(self):
  for i in range(241):
   t=.5+i/240
   e,o=pairs(t).values();self.assertAlmostEqual(e[0][0],-e[1][0]);self.assertAlmostEqual(e[0][1],e[1][1]);self.assertAlmostEqual(o[0][0],-o[1][0]);self.assertAlmostEqual(o[0][1],-o[1][1])
 def test_decomposition(self):
  for i in range(-50,51):
   x=i/10;a,b=decompose(x);self.assertAlmostEqual(a,x*x+2);self.assertAlmostEqual(b,3*x);self.assertAlmostEqual(a+b,x*x+3*x+2)
 def test_domains(self):
  d=[-2,-1,1,2];self.assertTrue(all(-x in d for x in d));self.assertNotIn(-2,[0,1,2,3])
 def test_counterexample(self):
  f=lambda x:x*x+x*(x*x-1)
  self.assertEqual(f(1),f(-1));self.assertNotEqual(f(2),f(-2));self.assertNotEqual(f(2),-f(-2))
if __name__=='__main__':unittest.main()
