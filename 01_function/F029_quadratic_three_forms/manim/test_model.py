import unittest
from model import value,expanded,vertex
class ModelTest(unittest.TestCase):
 def test_three_forms(self):
  for a in [-2,-1,.25,1,2]:
   for j in range(-100,101):
    x=j/20
    self.assertAlmostEqual(value(x,a),expanded(x,a))
    self.assertAlmostEqual(value(x,a),a*(x-2)**2-a)
 def test_roots_symmetry_extremum(self):
  for a in [-2,-1,.25,1,2]:
   self.assertEqual(value(1,a),0);self.assertEqual(value(3,a),0)
   h,k=vertex(a)
   for j in range(101):
    t=j/25
    self.assertAlmostEqual(value(h-t,a),value(h+t,a))
    self.assertGreaterEqual((value(h+t,a)-k)*a,-1e-12)
 def test_excludes_zero(self):
  with self.assertRaises(ValueError):value(2,0)
if __name__=='__main__':unittest.main()
