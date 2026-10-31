import math
import unittest
from model import ConfocalPair, SWEEP


class TestC094(unittest.TestCase):
    def test_all_four_points_over_sweep_and_general_parameters(self):
        for ae,c in ((4,2),(5,3),(6,3),(2.01,2),(20,0.2)):
            for i in range(1,200):
                model=ConfocalPair(ae,c,c*i/200)
                self.assertEqual(len(set(model.points())),4)
                for point in model.points():
                    self.assertNotEqual(point[0]*point[1],0)
                    for r in model.residuals(point):
                        self.assertAlmostEqual(r,0,places=9)
                    r1,r2=model.focal_distances(point)
                    self.assertAlmostEqual(r1+r2,2*ae,places=10)
                    self.assertAlmostEqual(abs(r1-r2),2*model.a_h,places=9)
                    x,y=point
                    self.assertAlmostEqual(r1*r1-r2*r2,4*c*x,places=9)
                    self.assertAlmostEqual(x*x+y*y,ae*ae+model.a_h**2-c*c,places=9)

    def test_displayed_reference_example(self):
        model=ConfocalPair()
        for actual,expected in zip(model.points(),((2,3),(2,-3),(-2,3),(-2,-3))):
            for a,e in zip(actual,expected):
                self.assertAlmostEqual(a,e,places=12)
        for actual,expected in zip(model.focal_distances((2,3)),(5,3)):
            self.assertAlmostEqual(actual,expected,places=12)

    def test_actual_curve_samples_and_shared_foci(self):
        for ah in SWEEP:
            m=ConfocalPair(a_h=ah)
            self.assertAlmostEqual(m.a_e**2-m.b_e**2,m.c**2)
            self.assertAlmostEqual(m.a_h**2+m.b_h**2,m.c**2)
            for i in range(121):
                x,y=m.ellipse(2*math.pi*i/120)
                self.assertAlmostEqual(x*x/m.a_e**2+y*y/m.b_e**2,1)
                for branch in (-1,1):
                    x,y=m.hyperbola(-3.8+i*7.6/120,branch)
                    self.assertAlmostEqual(x*x/m.a_h**2-y*y/m.b_h**2,1)

    def test_invalid_and_degenerate_states_rejected(self):
        for args in ((4,2,0),(4,2,2),(2,2,1),(4,0,1),(4,2,-1),(4,2,float('nan'))):
            with self.assertRaises(ValueError):
                ConfocalPair(*args)

    def test_independent_linear_elimination(self):
        # Solve the two original standard equations without the coordinate formula.
        for ah in SWEEP:
            m=ConfocalPair(a_h=ah)
            a,b=1/m.a_e**2,1/m.b_e**2
            c,d=1/m.a_h**2,-1/m.b_h**2
            determinant=a*d-b*c
            u=(d-b)/determinant
            v=(a-c)/determinant
            x,y=m.positive_point
            self.assertLess(determinant,0)
            self.assertAlmostEqual(x*x,u)
            self.assertAlmostEqual(y*y,v)

    def test_curve_window_contains_four_intersections_without_clipping(self):
        for i in range(241):
            m=ConfocalPair(a_h=.65+i/240)
            ymax=m.visible_hyperbola_y()
            x,y=m.positive_point
            self.assertGreater(ymax,y)
            self.assertLessEqual(abs(m.hyperbola(ymax)[0]),4.3+1e-12)
            self.assertLessEqual(ymax,3.8)


if __name__=='__main__':
    unittest.main()
