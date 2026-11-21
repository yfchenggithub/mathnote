import unittest
from model import f,segment
class Model(unittest.TestCase):
 def test_all_symmetries(self):
  for i in range(-1000,1001):
   x=i/71;self.assertAlmostEqual(f(-x),-f(x));self.assertAlmostEqual(f(2-x),f(x));self.assertAlmostEqual(f(x+2),-f(x));self.assertAlmostEqual(f(x+4),f(x))
 def test_segments(self):
  for n in range(-8,9):
   p,q=segment(n)
   for j in range(11):
    t=j/10;self.assertAlmostEqual(f(n+t),(1-t)*p[1]+t*q[1])
 def test_example(self):self.assertAlmostEqual(f(2026.5),-.5)
if __name__=='__main__':unittest.main()
