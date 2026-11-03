import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_tangents_midpoint_area(self):
        for i in range(501):
            t=-.45+.9*i/500;d=.8+.5*i/500
            A,B,P,M=state(t,d)
            for x,y in (A,B):
                self.assertAlmostEqual(x*x,2*p*y)
                self.assertAlmostEqual(x*P[0],p*(P[1]+y))
            self.assertAlmostEqual(P[0],M[0])
            self.assertAlmostEqual(area(t,d),abs(A[0]-B[0])**3/(8*p))

    def test_curve_intersection_bisects_median(self):
        for i in range(41):
            for j in range(41):
                t, d = -.45 + .9*i/40, .8 + .5*j/40
                A, B, P, M = state(t, d)
                N, PN, NM = midpoint_state(t, d)
                self.assertAlmostEqual(N[0]**2, 2*p*N[1])
                self.assertAlmostEqual(N[0], P[0])
                self.assertAlmostEqual(N[0], M[0])
                self.assertLess(P[1], N[1])
                self.assertLess(N[1], M[1])
                self.assertAlmostEqual(PN, NM)
                self.assertAlmostEqual(PN, (A[0]-B[0])**2/(8*p))
                self.assertAlmostEqual(PN+NM, M[1]-P[1])
                self.assertAlmostEqual(N[1], (P[1]+M[1])/2)
                self.assertEqual(rounded_for_display(PN), rounded_for_display(NM))

    def test_display_rounding_at_halfway_value(self):
        self.assertEqual(rounded_for_display(.8450000000000001), .85)
        self.assertEqual(rounded_for_display(.8449999999999999), .85)

    def test_small_and_wide_chords(self):
        for t in (-3., 0., 2.):
            for d in (.001, .8, 1.3, 4.):
                N, PN, NM = midpoint_state(t, d)
                self.assertAlmostEqual(PN, d*d/(2*p))
                self.assertAlmostEqual(NM, d*d/(2*p))

    def test_distinct_cut_points_required(self):
        for d in (0., -1.):
            with self.assertRaises(ValueError):
                midpoint_state(0., d)

if __name__=="__main__": unittest.main()
