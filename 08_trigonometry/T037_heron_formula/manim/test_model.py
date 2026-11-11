"""Mathematical acceptance for all T037 animation states, not renderer mocks."""
import unittest
from math import sqrt
import random
from model import Triangle, distance, coordinate_area, varying_base, equilateral, right_triangle


class HeronTests(unittest.TestCase):
    def check_triangle(self,t):
        for measured,expected in zip((distance(t.B,t.C),distance(t.C,t.A),distance(t.A,t.B)),(t.a,t.b,t.c)):
            self.assertAlmostEqual(measured,expected,places=9)
        self.assertAlmostEqual(t.S,coordinate_area(t.A,t.B,t.C),places=8)
        self.assertAlmostEqual(16*t.S*t.S,(t.a+t.b+t.c)*(t.a+t.b-t.c)*(t.a-t.b+t.c)*(-t.a+t.b+t.c),places=6)
        for h,u,v in zip(t.feet,(t.B,t.C,t.A),(t.C,t.A,t.B)):
            self.assertAlmostEqual(distance(t.I,h),t.r,places=8)
            self.assertAlmostEqual((t.I[0]-h[0])*(v[0]-u[0])+(t.I[1]-h[1])*(v[1]-u[1]),0.,places=8)
            self.assertAlmostEqual(distance(u,h)+distance(h,v),distance(u,v),places=8)
        D,E,F=t.feet
        _,x,y,z=t.factors
        for measured,expected in ((distance(t.A,E),x),(distance(t.A,F),x),(distance(t.B,D),y),(distance(t.B,F),y),(distance(t.C,D),z),(distance(t.C,E),z)):
            self.assertAlmostEqual(measured,expected,places=8)
        self.assertAlmostEqual(sum(coordinate_area(t.I,u,v) for u,v in ((t.B,t.C),(t.C,t.A),(t.A,t.B))),t.S,places=8)
        self.assertAlmostEqual(t.r*t.r*t.p,x*y*z,places=8)

    def test_entire_base_motion(self):
        for i in range(361):
            self.check_triangle(varying_base(7+3*i/360))

    def test_equilateral_motion(self):
        for i in range(121):
            t=equilateral(4+2*i/120)
            self.check_triangle(t)
            self.assertAlmostEqual(t.S,sqrt(3)*t.a*t.a/4,places=9)

    def test_right_factor_pairing(self):
        for a,b in ((3,4),(1,1),(5,12),(.5,3),(8,15)):
            t=right_triangle(a,b); self.check_triangle(t)
            p,x,y,z=t.factors
            self.assertAlmostEqual(p*z,a*b/2,places=9)
            self.assertAlmostEqual(x*y,a*b/2,places=9)
            self.assertAlmostEqual(t.S,a*b/2,places=9)
            self.assertAlmostEqual((t.A[0]-t.C[0])*(t.B[0]-t.C[0])+(t.A[1]-t.C[1])*(t.B[1]-t.C[1]),0,places=9)

    def test_source_numeric_examples(self):
        for sides,expected in (((5,6,7),6*sqrt(6)),((13,14,15),84),((5,5,6),12),((9,10,17),36),((3,4,5),6),((6,6,6),9*sqrt(3))):
            t=Triangle(*sides);self.check_triangle(t);self.assertAlmostEqual(t.S,expected,places=9)
        t=Triangle(13,14,15)
        self.assertEqual(t.factors,(21,8,7,6))
        self.assertEqual(t.r,4)
        self.assertAlmostEqual(t.C[0],8.4)
        self.assertAlmostEqual(t.C[1],11.2)

    def test_random_positive_tangent_lengths(self):
        rng=random.Random(37)
        for _ in range(100):
            x,y,z=[rng.uniform(.5,8) for _ in range(3)]
            self.check_triangle(Triangle(y+z,z+x,x+y))

    def test_invalid_and_degenerate(self):
        for sides in ((0,3,3),(-1,3,3),(2,3,5),(3,4,8),(float('nan'),4,5),(float('inf'),4,5)):
            with self.assertRaises(ValueError):Triangle(*sides)


if __name__=='__main__':unittest.main()
