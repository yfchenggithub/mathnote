import unittest
from fractions import Fraction as F
import model_nine as m

class NinePathsMath(unittest.TestCase):
    def test_all_nine_formal_cases(self):
        self.assertEqual(len(set(m.CASES)),9)
        self.assertEqual(m.CASES[2],(1,-1))
        self.assertEqual(m.CASES[6],(-1,1))
        self.assertEqual({(m.trend(a),m.trend(b)) for a,b in m.CASES},{(x,y) for x in ['升','平','降'] for y in ['升','平','降']})
    def test_continuity_and_two_sided_derivative(self):
        for a,b in m.CASES:
            self.assertEqual(m.f(0,a,b),0)
            self.assertEqual(m.df(0,a,b),0)
            for n in range(1,12):
                for sign in [-1,1]:
                    h=sign*F(1,2**n)
                    self.assertEqual((m.f(h,a,b)-m.f(0,a,b))/h,m.quotient(h,a,b))
                    self.assertLessEqual(abs(m.quotient(h,a,b)),h*h)
                    self.assertLessEqual(abs(m.f(h,a,b)),abs(h)**3)
    def test_each_side_has_the_claimed_direction(self):
        for a,b in m.CASES:
            for xs,k in [([F(i,20) for i in range(-20,0)],a),([F(i,20) for i in range(1,21)],b)]:
                for x,y in zip(xs,xs[1:]):
                    delta=m.f(y,a,b)-m.f(x,a,b)
                    self.assertEqual((delta>0)-(delta<0),k)
                    slope=m.df(x,a,b)
                    self.assertEqual((slope>0)-(slope<0),k)
    def test_tangent_model_through_every_scan_position(self):
        for a,b in m.CASES:
            for i in range(191):
                x=-.95+i*.01;p,q=m.tangent_endpoints(x,a,b)
                self.assertAlmostEqual((p[0]+q[0])/2,x,places=13)
                self.assertAlmostEqual((p[1]+q[1])/2,m.f(x,a,b),places=13)
                self.assertAlmostEqual((q[1]-p[1])/(q[0]-p[0]),m.df(x,a,b),places=12)
                self.assertTrue(all(abs(xx)<1.35 and abs(yy)<1.5 for xx,yy in [p,q]))
    def test_turns_flat_pieces_and_rolle_are_not_confused(self):
        turning=[(a,b) for a,b in m.CASES if a*b<0]
        self.assertEqual(set(turning),{(1,-1),(-1,1)})
        # A one-sided plateau can still give a non-strict local extremum.
        for a,b in [(1,0),(0,-1)]:
            self.assertTrue(all(m.f(x,a,b)<=0 for x in [-.1,0,.1]))
        for a,b in [(-1,0),(0,1)]:
            self.assertTrue(all(m.f(x,a,b)>=0 for x in [-.1,0,.1]))
        self.assertEqual([p for p in m.CASES if m.f(-1,*p)==m.f(1,*p)],[(1,-1),(0,0),(-1,1)])

if __name__=='__main__':unittest.main(verbosity=2)
