"""Verify curves, foci, tangent equations and right angles independently."""
import unittest
from math import hypot, sqrt
from model import ConfocalPair


class GeometryTests(unittest.TestCase):
    def test_full_motion_and_all_quadrants(self):
        for i in range(181):
            m = ConfocalPair(A=.65 + .9*i/180)
            self.assertAlmostEqual(m.A*m.A+m.B2, m.c*m.c)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    x,y=m.point(sx,sy)
                    self.assertAlmostEqual(x*x/m.a**2+y*y/m.b2,1)
                    self.assertAlmostEqual(x*x/m.A**2-y*y/m.B2,1)
                    r1,r2=hypot(x+m.c,y),hypot(x-m.c,y)
                    self.assertAlmostEqual(r1+r2,2*m.a)
                    self.assertAlmostEqual(abs(r1-r2),2*m.A)
                    e,h=m.directions(sx,sy)
                    self.assertAlmostEqual(e[0]*x/m.a**2+e[1]*y/m.b2,0)
                    self.assertAlmostEqual(h[0]*x/m.A**2-h[1]*y/m.B2,0)
                    self.assertAlmostEqual(e[0]*h[0]+e[1]*h[1],0)
                    ke,kh=m.slopes(sx,sy)
                    self.assertAlmostEqual(ke*kh,-1)
                    # Focal angle bisectors: normals are parallel to unit-vector sum/difference.
                    u=((x+m.c)/r1,y/r1); v=((x-m.c)/r2,y/r2)
                    self.assertAlmostEqual((u[0]+v[0])*e[0]+(u[1]+v[1])*e[1],0)
                    self.assertAlmostEqual((u[0]-v[0])*h[0]+(u[1]-v[1])*h[1],0)

    def test_reference_and_boundaries(self):
        self.assertEqual(ConfocalPair().point(),(2,3))
        self.assertEqual(ConfocalPair().slopes(),(-.5,2))
        for A in (.00001,1.99999):
            m=ConfocalPair(A=A)
            ke,kh=m.slopes()
            self.assertAlmostEqual(ke*kh,-1)
        for args in ({'A':0},{'A':2},{'c':4},{'c':0}):
            with self.assertRaises(ValueError): ConfocalPair(**args)

    def test_visible_curve_samples(self):
        for A in (.65,1,1.55):
            m=ConfocalPair(A=A)
            ymax=min(4.1,sqrt(m.B2)*sqrt((4.35/A)**2-1))
            for j in range(101):
                y=-ymax+2*ymax*j/100
                for sign in (-1,1):
                    x=m.hyperbola_x(y,sign)
                    self.assertLessEqual(abs(x),4.3500001)
                    self.assertAlmostEqual(x*x/m.A**2-y*y/m.B2,1)


if __name__=='__main__': unittest.main()
