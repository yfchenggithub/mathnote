import unittest
import model

class TangentClosureTests(unittest.TestCase):
    def test_tangency_feet_and_vertical_critical_state(self):
        self.assertGreater(model.audit(),700)

    def test_excluded_parameters(self):
        for a in [-1,1]:
            with self.assertRaises(ValueError):model.state(a)
        with self.assertRaises(ValueError):model.state(0,k=0)

if __name__=='__main__':unittest.main()
