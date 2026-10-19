from math import cos, pi, sin, sqrt
import unittest
from model import FocalBoundModel, START, RIGHT_THRESHOLD, ANGLE120_THRESHOLD


class BoundTests(unittest.TestCase):
    def test_geometry_inequality_and_exact_gap(self):
        for e in (.01,.5,.6,RIGHT_THRESHOLD,ANGLE120_THRESHOLD,.9,.999):
            m = FocalBoundModel(e=e)
            for i in range(721):
                t = i*pi/360
                x,y = m.point(t)
                r1,r2 = m.radii(t)
                theta = m.angle(t)
                self.assertAlmostEqual(x*x/m.a**2+y*y/m.b**2,1,places=12)
                self.assertAlmostEqual(r1+r2,2*m.a,places=11)
                self.assertLessEqual(m.half_sine(t),e+1e-12)
                self.assertAlmostEqual(sin(theta/2)**2,1-m.b**2/(r1*r2),places=11)
                gap = (r1-r2)**2/(4*m.a**2)*cos(theta/2)**2
                self.assertAlmostEqual(e*e-sin(theta/2)**2,gap,places=11)
                self.assertLessEqual(theta,m.maximum+1e-12)

    def test_equality_only_at_both_minor_vertices(self):
        m = FocalBoundModel()
        for t in (pi/2,3*pi/2):
            self.assertAlmostEqual(m.half_sine(t),m.e,places=12)
            r1,r2=m.radii(t)
            self.assertAlmostEqual(r1,r2,places=12)
        for t in (0,.2,START,pi,4,2*pi):
            self.assertLess(m.half_sine(t),m.e)
        for t in (0,pi,2*pi):
            self.assertAlmostEqual(m.angle(t),0,places=12)

    def test_formal_numeric_examples(self):
        m = FocalBoundModel()
        self.assertAlmostEqual(m.point(START)[0],3,places=12)
        self.assertAlmostEqual(m.point(START)[1],16/5,places=12)
        self.assertAlmostEqual(m.half_sine(START),3/sqrt(34),places=12)
        self.assertAlmostEqual(m.maximum*180/pi,73.739795291688,places=10)
        self.assertAlmostEqual(FocalBoundModel(e=.5).maximum,pi/3,places=12)

    def test_thresholds_and_inverse_existence(self):
        self.assertAlmostEqual(FocalBoundModel(e=RIGHT_THRESHOLD).maximum,pi/2,places=12)
        self.assertAlmostEqual(FocalBoundModel(e=ANGLE120_THRESHOLD).maximum,2*pi/3,places=12)
        for e in (.3,.6,RIGHT_THRESHOLD,.8,ANGLE120_THRESHOLD,.9):
            m=FocalBoundModel(e=e)
            for degrees in (0,30,60,90,120,150):
                target=degrees*pi/180
                t=m.parameter_for_angle(target)
                expected=e+1e-12 >= sin(target/2)
                self.assertEqual(t is not None,expected)
                if t is not None:
                    self.assertAlmostEqual(m.angle(t),target,places=10)

    def test_shape_change_preserves_a_and_increases_maximum(self):
        shapes=[FocalBoundModel(e=.6+i*.003) for i in range(101)]
        for first,second in zip(shapes,shapes[1:]):
            self.assertEqual(first.a,second.a)
            self.assertLess(second.b,first.b)
            self.assertGreater(second.c,first.c)
            self.assertGreater(second.maximum,first.maximum)

    def test_invalid_domain(self):
        for a,e in [(0,.6),(5,0),(5,1),(5,-.1),(float('inf'),.5)]:
            with self.assertRaises(ValueError):
                FocalBoundModel(a,e)
        for target in (-.1,pi):
            with self.assertRaises(ValueError):
                FocalBoundModel().parameter_for_angle(target)


if __name__=='__main__':
    unittest.main()
