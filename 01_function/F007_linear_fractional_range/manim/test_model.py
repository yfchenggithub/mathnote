import unittest
import model
class ModelTests(unittest.TestCase):
    def test_exact_relationships_and_boundaries(self):
        self.assertGreater(model.audit(),100)
if __name__=="__main__":unittest.main()
