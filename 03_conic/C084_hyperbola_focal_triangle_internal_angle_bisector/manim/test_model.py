import unittest,math
from fractions import Fraction as F
from model import FocalState,state,clip_line,direction,sweep

class C084ModelTests(unittest.TestCase):
    def close(self,a,b):self.assertAlmostEqual(a,b,delta=2e-7*max(1,abs(a),abs(b)))

    def test_invariants_and_both_bisectors(self):
        for a,b in [(3,4),(1,1),(2,3)]:
            for branch in [-1,1]:
                for upper in [-1,1]:
                    for t in [.001,.1,.4,math.log(2),1.2,2.5]:
                        s=state(t,a,b,branch,upper);u,v=s.units
                        self.close(s.x*s.m,a*a)
                        self.close(abs(s.r1-s.r2),2*a)
                        self.close((s.c+s.m)/(s.c-s.m),s.r1/s.r2)
                        self.assertLess(abs(s.m),a);self.assertGreater(abs(s.n),s.c)
                        w=(s.m-s.x,-s.y)
                        self.close((u[0]+v[0])*w[1]-(u[1]+v[1])*w[0],0)
                        self.assertGreater((u[0]+v[0])*w[0]+(u[1]+v[1])*w[1],0)
                        self.close(w[0]*s.normal[0]+w[1]*s.normal[1],0)
                        self.close((s.n-s.x)*s.tangent[0]-s.y*s.tangent[1],0)

    def test_every_motion_frame_and_angle(self):
        for i in range(385):
            s=state(.45+(1.15-.45)*i/384)
            q1=direction(s.p,s.f1);qm=direction(s.p,(s.m,0));q2=direction(s.p,s.f2)
            self.close(sweep(q1,qm),sweep(qm,q2))
            for p in clip_line(s.p,s.tangent,(-5.6,5.8,-1.4,6.7)):
                self.close(s.x*p[0]/9-s.y*p[1]/16,1)

    def test_vertical_focal_lines(self):
        for sign in [-1,1]:
            s=FocalState(3,4,sign*5,16/3)
            D1=(s.x-s.m)*(s.x+s.c)+s.y*s.y
            D2=(s.x-s.m)*(s.x-s.c)+s.y*s.y
            self.close(s.y*(s.c+s.m)/D1,s.y*(s.c-s.m)/D2)

    def test_exact_example_and_two_roots(self):
        s=state(math.log(2));self.close(s.x,15/4);self.close(s.y,3)
        self.close(s.m,12/5);self.close(s.n,125/12)
        x=F(15,4);y=F(3);a=F(3);c=F(5)
        for m in [a*a/x,c*c*x/(a*a)]:
            k=y/(x-m);k1=y/(x+c);k2=y/(x-c)
            self.assertEqual((k-k1)/(1+k*k1),(k2-k)/(1+k2*k))
            self.assertEqual((m*x-a*a)*(c*c*x-a*a*m),0)

    def test_reject_degenerate_and_invalid(self):
        for args in [(3,4,3,0),(0,4,3,2),(3,4,4,3)]:
            with self.assertRaises(ValueError):FocalState(*args)
        with self.assertRaises(ValueError):state(0)

if __name__=='__main__':unittest.main()
