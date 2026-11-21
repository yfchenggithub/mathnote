import unittest
from model import *
class ModelTests(unittest.TestCase):
    def test_two_inputs_merge(self):
        for k in range(101):
            t=.4+k/100
            self.assertAlmostEqual(inner(-t),inner(t))
            self.assertAlmostEqual(composite(-t),composite(t))
            self.assertAlmostEqual(composite(t),2**(t*t))
    def test_outer_is_not_even_or_odd(self):
        self.assertNotEqual(outer(-1),outer(1))
        self.assertNotEqual(outer(-1),-outer(1))
    def test_domains(self):
        for t in [.4,1,1.4]:
            s=state(t);self.assertGreaterEqual(s["u_plus"],0);self.assertLessEqual(s["value"],5.5)
if __name__=="__main__":unittest.main()
