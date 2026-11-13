import unittest
from math import pi, cos, sin, hypot
from model import reflect, slope, ORIGINAL, VERTICAL_ALPHA

class ReflectionTests(unittest.TestCase):
    def test_special_mirrors(self):
        for a, expected in [(0,(2,-1)),(pi/4,(1,2)),(pi/2,(-2,1)),(-pi/4,(-1,-2))]:
            for actual, target in zip(reflect(ORIGINAL,a),expected):
                self.assertAlmostEqual(actual,target)
    def test_vertical_boundary(self):
        v=reflect(ORIGINAL,VERTICAL_ALPHA)
        self.assertIsNone(slope(v))
        self.assertAlmostEqual(v[1],hypot(*ORIGINAL))
    def test_full_motion(self):
        for i in range(361):
            a=i*pi/720
            v=reflect(ORIGINAL,a)
            self.assertAlmostEqual(hypot(*v),hypot(*ORIGINAL))
            self.assertAlmostEqual(v[0]*cos(a)+v[1]*sin(a),2*cos(a)+sin(a))
            self.assertAlmostEqual(v[0]*(-sin(a))+v[1]*cos(a),-(2*(-sin(a))+cos(a)))
            for x,y in zip(reflect(v,a),ORIGINAL): self.assertAlmostEqual(x,y)
            m=sin(a)/cos(a)
            if abs(cos(a))>1e-8 and abs(v[0])>1e-8:
                self.assertAlmostEqual(slope(v),(2*m+(m*m-1)*.5)/(1-m*m+m),places=7)

if __name__=='__main__': unittest.main()
