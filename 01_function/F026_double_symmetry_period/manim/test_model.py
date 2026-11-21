import unittest
from model import f,state
class Model(unittest.TestCase):
 def test_symmetries(self):
  for i in range(-800,801):
   x=i/47;self.assertAlmostEqual(f(-x),f(x));self.assertAlmostEqual(f(4-x),f(x));self.assertAlmostEqual(f(x+4),f(x))
 def test_composition(self):
  for i in range(201):
   p,q,r=state(.3+i*.0045);self.assertAlmostEqual(p[0]+q[0],0);self.assertAlmostEqual(q[0]+r[0],4);self.assertAlmostEqual(r[0]-p[0],4);self.assertAlmostEqual(p[1],r[1])
 def test_not_half_period(self):self.assertAlmostEqual(f(0),1);self.assertAlmostEqual(f(2),-1)
if __name__=='__main__':unittest.main()
