import unittest,math
from model import value,slope_at_common_point,visible_domain,shifted

class F038ModelTests(unittest.TestCase):
    def test_common_point_positive_and_reciprocal(self):
        for a in [.25,.5,.8,1,1.2,2,4]:
            self.assertEqual(value(a,0),1)
            for x in [-8,-2,-.3,0,.7,2,8]:
                self.assertGreater(value(a,x),0)
                self.assertAlmostEqual(value(a,x),value(1/a,-x))
                self.assertAlmostEqual(value(a,x+1)/value(a,x),a)

    def test_monotonicity_and_ratio(self):
        for a in [.25,.5,.8,1.2,2,4]:
            for x1 in [-2,-.7,0,.3,2]:
                for d in [.1,.5,1,2.3]:
                    self.assertAlmostEqual(value(a,x1+d)/value(a,x1),value(a,d))
                    self.assertEqual(value(a,x1+d)>value(a,x1),a>1)

    def test_base_order_and_clockwise_tangent(self):
        last=None
        for i in range(401):
            beta=math.log(4)*(1-i/200);a=math.exp(beta)
            angle=math.atan(slope_at_common_point(a))
            if last:
                olda,oldangle=last
                self.assertLess(angle,oldangle)
                self.assertLess(value(a,1),value(olda,1))
                self.assertGreater(value(a,-1),value(olda,-1))
            last=a,angle
            lo,hi=visible_domain(a)
            for j in range(31):
                x=lo+(hi-lo)*j/30;y=value(a,x)
                self.assertGreater(y,0);self.assertLessEqual(y,4.8+1e-9)
            eps=1e-5
            self.assertAlmostEqual((value(a,eps)-value(a,-eps))/(2*eps),beta,places=8)

    def test_examples_and_endpoints(self):
        self.assertLess(value(1.7,.3),value(1.7,.5))
        self.assertGreater(value(.5,.8),value(.5,1.2))
        for x in [-2,0,1,1.9,2,2.1,3]:
            self.assertEqual(value(2,x)>value(4,x-1),x<2)
        for a in [.5,2]:
            for x in [-1,0,1,2,3,4]:
                self.assertEqual(value(a,x*x-3*x)>1,(x<0 or x>3) if a>1 else (0<x<3))
        self.assertEqual(shifted(2,1,1,3),4)
        self.assertEqual(shifted(.25,-2,-2,-1),0)
        self.assertLess(value(2,3),value(3,2))
        for x in [-1,0,2.9,3,3.1,4]:
            self.assertEqual(value(1/3,2*x-1)>=value(1/3,x+2),x<=3)

    def test_asymptote_and_invalid_base(self):
        self.assertGreater(value(.5,20),0)
        self.assertLess(value(.5,20),1e-6)
        for a in [0,-2]:
            with self.assertRaises(ValueError):value(a,.5)

if __name__=='__main__':unittest.main()
