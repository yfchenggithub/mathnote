from math import cos,pi,sin,sqrt
import unittest
from model import PointTangentModel,clip_line


class PointFormulaTests(unittest.TestCase):
    def test_full_orbit_tangency_and_drawing(self):
        for a,b in [(2,1),(3,2),(sqrt(8),sqrt(2))]:
            m=PointTangentModel(a,b)
            for i in range(721):
                t=i*pi/360; p=m.point(t); A,B,C=m.tangent(t)
                self.assertAlmostEqual(m.position(p),1,places=12)
                self.assertAlmostEqual(A*p[0]+B*p[1],C,places=12)
                self.assertAlmostEqual(a*a*A*A+b*b*B*B,C*C,places=12)
                self.assertAlmostEqual(A*(-a*sin(t))+B*b*cos(t),0,places=12)
                for dt in (.1,.4,1,pi):
                    q=m.point(t+dt)
                    self.assertLess(A*q[0]+B*q[1],C)
        m=PointTangentModel()
        for i in range(721):
            coeff=m.tangent(i*pi/360); ends=clip_line(*coeff)
            self.assertEqual(len(ends),2)
            A,B,C=coeff
            for x,y in ends:
                self.assertAlmostEqual(A*x+B*y,C,places=11)

    def test_axis_endpoints_include_vertical_tangents(self):
        m=PointTangentModel()
        for t,expected in [(0,(.5,0,1)),(pi/2,(0,1,1)),(pi,(-.5,0,1)),(3*pi/2,(0,-1,1))]:
            for actual,target in zip(m.tangent(t),expected):
                self.assertAlmostEqual(actual,target,places=12)

    def test_formal_known_point_example(self):
        m=PointTangentModel(sqrt(8),sqrt(2))
        self.assertAlmostEqual(m.position((2,1)),1,places=12)
        A,B,C=m.tangent_at((2,1))
        self.assertAlmostEqual(A,.25,places=12)
        self.assertAlmostEqual(B,.5,places=12)
        self.assertEqual(C,1)
        # The ellipse normal is not generally parallel to OP.
        self.assertNotAlmostEqual(2*B-1*A,0)

    def test_formal_external_point_and_polar(self):
        m=PointTangentModel(); M=(2,2)
        self.assertEqual(m.position(M),5)
        contacts=sorted(m.contacts_from(M))
        for p,expected in zip(contacts,[(-1.2,.8),(2,0)]):
            for actual,target in zip(p,expected):
                self.assertAlmostEqual(actual,target,places=12)
            self.assertAlmostEqual(m.position(p),1,places=12)
            A,B,C=m.tangent_at(p)
            self.assertAlmostEqual(A*M[0]+B*M[1],C,places=12)
            A,B,C=m.polar(M)
            self.assertAlmostEqual(A*p[0]+B*p[1],C,places=12)
        A,B,C=m.polar(M)
        self.assertNotAlmostEqual(A*M[0]+B*M[1],C)

    def test_polar_position_cases(self):
        m=PointTangentModel()
        self.assertEqual(len(m.contacts_from((4,0))),2)
        self.assertEqual(len(m.contacts_from((2,0))),1)
        self.assertEqual(m.contacts_from((.5,0)),[])
        self.assertEqual(m.contacts_from((0,0)),[])
        self.assertIsNone(m.polar((0,0)))
        self.assertEqual(m.polar((.5,0)),(.125,0,1))  # x=8, outside the ellipse.

    def test_external_points_independent_contact_checks(self):
        m=PointTangentModel()
        for M in [(3,1),(-3,2),(1,3),(-1,-2),(4,0)]:
            for p in m.contacts_from(M):
                self.assertAlmostEqual(m.position(p),1,places=12)
                A,B,C=m.tangent_at(p)
                self.assertAlmostEqual(A*M[0]+B*M[1],C,places=12)

    def test_invalid_tangent_point_and_axes(self):
        with self.assertRaises(ValueError):
            PointTangentModel().tangent_at((2,2))
        for a,b in [(1,1),(1,2),(1,0)]:
            with self.assertRaises(ValueError):
                PointTangentModel(a,b)


if __name__=='__main__':
    unittest.main()
