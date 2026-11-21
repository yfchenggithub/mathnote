import unittest
from model import factor, product, state
class ModelTests(unittest.TestCase):
    def test_all_positions(self):
        for i in range(121):
            t=0.4+i/100
            s=state(t)
            self.assertAlmostEqual(s["left_factor"],-s["right_factor"])
            self.assertAlmostEqual(s["left_product"],s["right_product"])
            self.assertAlmostEqual(s["left_product"],t*t)
    def test_limits(self):
        for t in [0.4,1,1.6]:self.assertGreaterEqual(product(t),0)
        with self.assertRaises(ValueError):state(0)
if __name__=="__main__":unittest.main()
