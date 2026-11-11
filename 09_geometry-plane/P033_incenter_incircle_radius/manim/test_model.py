import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import Triangle, area, distance, equilateral, foot, lesson_triangle, moving_triangle, right_triangle

class TestP033(unittest.TestCase):
    def audit(self,t):
        a,b,c=t.sides
        for H,(U,V) in zip(t.feet,((t.B,t.C),(t.C,t.A),(t.A,t.B))):
            self.assertAlmostEqual(distance(t.I,H),t.r,places=9)
            self.assertAlmostEqual(sum((t.I[k]-H[k])*(V[k]-U[k]) for k in (0,1)),0,places=8)
            self.assertAlmostEqual(distance(U,H)+distance(H,V),distance(U,V),places=8)
        self.assertAlmostEqual(sum(t.pieces),t.S,places=9)
        for piece,side in zip(t.pieces,t.sides): self.assertAlmostEqual(piece,side*t.r/2,places=9)
        x,y,z=t.tangent_lengths
        self.assertTrue(min(x,y,z)>0)
        self.assertAlmostEqual(x+y,c);self.assertAlmostEqual(y+z,a);self.assertAlmostEqual(x+z,b)
        D,E,F=t.feet
        for V,feet,length in ((t.A,(E,F),x),(t.B,(F,D),y),(t.C,(D,E),z)):
            for H in feet:self.assertAlmostEqual(distance(V,H),length,places=8)

    def test_13_14_15(self):
        t=lesson_triangle();self.audit(t)
        self.assertEqual(t.sides,(14,13,15));self.assertEqual(t.I,(8,4))
        self.assertEqual(t.S,84);self.assertEqual(t.r,4);self.assertEqual(t.tangent_lengths,(7,8,6))

    def test_every_motion_state(self):
        for i in range(481):
            with self.subTest(frame=i):self.audit(moving_triangle(i/480))

    def test_motion_loop(self):
        for k in (0,1):self.assertAlmostEqual(moving_triangle(0).A[k],moving_triangle(1).A[k])

    def test_equilateral(self):
        for side in (.1,1,6,100):
            t=equilateral(side);self.audit(t)
            self.assertAlmostEqual(t.I[0],side/2);self.assertAlmostEqual(t.I[1],math.sqrt(3)*side/6)
            self.assertAlmostEqual(distance(t.A,t.I),2*t.r)
            for x in t.tangent_lengths:self.assertAlmostEqual(x,side/2)

    def test_right(self):
        for u,v in ((3,4),(5,12),(.2,9),(6,8)):
            t=right_triangle(u,v);self.audit(t)
            self.assertAlmostEqual(t.r,(u+v-math.hypot(u,v))/2)
            self.assertAlmostEqual(t.I[0],t.r);self.assertAlmostEqual(t.I[1],t.r)
            self.assertAlmostEqual(t.tangent_lengths[1],t.r)

    def test_isosceles_right(self):
        for side in (.1,2,4,20):
            t=right_triangle(side,side);self.audit(t)
            self.assertAlmostEqual(t.r,(2-math.sqrt(2))*side/2)
            self.assertAlmostEqual(t.r,(math.sqrt(2)-1)*t.sides[1]/2)
            self.assertAlmostEqual(t.tangent_lengths[0],side/math.sqrt(2))
            self.assertAlmostEqual(t.tangent_lengths[2],side/math.sqrt(2))

    def test_rigid_transform(self):
        t=lesson_triangle();angle=.73
        def move(p):return (3+p[0]*math.cos(angle)-p[1]*math.sin(angle),-2+p[0]*math.sin(angle)+p[1]*math.cos(angle))
        u=Triangle(*(move(p) for p in (t.A,t.B,t.C)));self.audit(u)
        self.assertAlmostEqual(u.r,t.r)
        for p,q in zip(u.I,move(t.I)):self.assertAlmostEqual(p,q)

    def test_invalid_geometry(self):
        with self.assertRaises(ValueError):Triangle((0,0),(1,0),(2,0))
        with self.assertRaises(ValueError):right_triangle(0,4)
        with self.assertRaises(ValueError):equilateral(-1)

if __name__=='__main__':unittest.main()
