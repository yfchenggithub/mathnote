import unittest
import model

class SlopeRelationTests(unittest.TestCase):
    def test_orientations_and_critical_chords(self):
        self.assertGreater(model.audit(),1800)

    def test_undefined_is_not_zero(self):
        A,B=model.state(-2)
        self.assertIsNone(model.slope(A,B))
        A,B=model.state(-2,True)
        self.assertEqual(model.slope(A,B),0)

if __name__=='__main__':unittest.main()
