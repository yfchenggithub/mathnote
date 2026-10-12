import math
import unittest

from .model import Ellipse, validation_results


class EllipseChordTests(unittest.TestCase):
    def test_all_directions_both_foci(self):
        for e in (Ellipse(3,2),Ellipse(4,3),Ellipse(5,4)):
            for side in (-1,1):
                for k in (0,1,-1,2,None):
                    with self.subTest(a=e.a,b=e.b,side=side,k=k):
                        result=e.validate_case(k,side)
                        self.assertAlmostEqual(result["distance"],result["formula"])

    def test_quadratic_and_root_difference(self):
        result=validation_results()
        q=result["quadratic"]
        self.assertAlmostEqual(q["discriminant"],4*9*16*2)
        self.assertAlmostEqual(math.sqrt(q["discriminant"])/q["A"],
                               e_dist := Ellipse(3,2).distance(1)/math.sqrt(2))
        self.assertAlmostEqual(e_dist*math.sqrt(2),48/13)

    def test_latus_rectum(self):
        e=Ellipse(3,2)
        for side in (-1,1):
            p,q=e.intersections(None,side)
            self.assertEqual(p[0],side*math.sqrt(5))
            self.assertAlmostEqual(p[1],-4/3)
            self.assertAlmostEqual(q[1],4/3)
            self.assertAlmostEqual(e.distance(None,side),8/3)

    def test_parameter_guards(self):
        with self.assertRaises(ValueError): Ellipse(2,3)
        with self.assertRaises(ValueError): Ellipse(3,2).focus(0)


if __name__=="__main__":unittest.main()
