from math import sqrt
import unittest
from model import SlopeRangeModel,clip_line


class SlopeRangeTests(unittest.TestCase):
    def assert_tangent(self,m,line,point,external=None):
        A,B,C=line; x,y=point
        self.assertAlmostEqual(m.position(point),1,places=11)
        self.assertAlmostEqual(A*x+B*y,C,places=11)
        self.assertAlmostEqual(m.a*m.a*A*A+m.b*m.b*B*B,C*C,places=10)
        if external is not None:
            self.assertAlmostEqual(A*external[0]+B*external[1],C,places=10)

    def test_arbitrary_finite_slope_has_two_parallel_tangents(self):
        m=SlopeRangeModel()
        for k in [-100,-4,-2,-1,-.1,0,.1,1,2,4,100]:
            pair=m.parallel_pair(k)
            self.assertEqual(len(pair),2)
            for line,point in pair:
                self.assert_tangent(m,line,point)
                A,B,C=line
                self.assertAlmostEqual(-A/B,k,places=12)
            self.assertEqual(pair[0][0][2],-pair[1][0][2])

    def test_fixed_point_quadratic_and_vieta(self):
        m=SlopeRangeModel()
        for p in [(0,2),(1,2),(3,1),(-3,-2),(1,sqrt(3)/2),(.5,0)]:
            roots=m.finite_roots(p); A,B,C=m.slope_equation(p)
            for k in roots:
                intercept=p[1]-k*p[0]
                self.assertAlmostEqual(intercept**2,m.a*m.a*k*k+m.b*m.b,places=10)
            if len(roots)==2:
                self.assertAlmostEqual(sum(roots),-B/A,places=11)
                self.assertAlmostEqual(roots[0]*roots[1],C/A,places=11)
            D=B*B-4*A*C
            self.assertAlmostEqual(D,4*m.a*m.a*m.b*m.b*(m.position(p)-1),places=10)

    def test_formal_external_point_and_vertical_exception(self):
        m=SlopeRangeModel()
        roots=m.finite_roots((0,2))
        self.assertAlmostEqual(roots[0],-sqrt(3)/2,places=12)
        self.assertAlmostEqual(roots[1],sqrt(3)/2,places=12)
        self.assertEqual(m.finite_roots((2,2)),[3/8])
        tangents=m.point_tangents((2,2))
        self.assertEqual(len(tangents),2)
        self.assertTrue(any(abs(line[1])<1e-12 for line,_ in tangents))
        self.assertEqual(m.finite_roots((2,0)),[])
        self.assertEqual(len(m.point_tangents((2,0))),1)
        self.assertEqual(m.point_tangents((1,0)),[])

    def test_all_animated_point_states_and_clipping(self):
        m=SlopeRangeModel()
        points=[(2*i/200,2) for i in range(201)]+[(2,2-2*i/200) for i in range(201)]+[(2-i/100,0) for i in range(101)]
        for p in points:
            S=m.position(p)
            expected=1 if abs(S-1)<1e-12 else 2 if S>1 else 0
            tangents=m.point_tangents(p)
            self.assertEqual(len(tangents),expected)
            for line,point in tangents:
                self.assert_tangent(m,line,point,p)
                endpoints=clip_line(*line)
                self.assertEqual(len(endpoints),2)
                A,B,C=line
                for x,y in endpoints:
                    self.assertAlmostEqual(A*x+B*y,C,places=10)

    def test_total_line_count_vs_number_of_finite_slopes(self):
        m=SlopeRangeModel()
        for p in [(0,2),(1,2),(2,2),(2,1),(2,0),(-2,2),(1,0),(0,0)]:
            tangents=m.point_tangents(p)
            finite=sum(abs(line[1])>1e-10 for line,_ in tangents)
            self.assertEqual(finite,len(m.finite_roots(p)))

    def test_invalid_model_and_infinite_slope_rejected(self):
        for a,b in [(1,1),(1,2),(1,0)]:
            with self.assertRaises(ValueError):
                SlopeRangeModel(a,b)
        with self.assertRaises(ValueError):
            SlopeRangeModel().parallel_pair(float('inf'))


if __name__=='__main__':
    unittest.main()
