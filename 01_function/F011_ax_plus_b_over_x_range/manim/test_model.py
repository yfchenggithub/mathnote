import math
import unittest
from model import value, extrema, branch_points, branch_distance, support_distance, smooth_path


class F011MathTests(unittest.TestCase):
    def test_parameter_extrema_and_odd_symmetry(self):
        for A in (.2, 1, 3, 9):
            for B in (.3, 1, 4, 12):
                x0, y0=extrema(A,B)
                self.assertAlmostEqual(value(x0,A,B),y0)
                self.assertAlmostEqual(value(-x0,A,B),-y0)
                for x in (.05,.25,.5,1,2,4,20):
                    self.assertGreaterEqual(value(x,A,B)+1e-10,y0)
                    self.assertLessEqual(value(-x,A,B)-1e-10,-y0)
                    self.assertAlmostEqual(value(x,A,B),-value(-x,A,B))

    def test_range_sweep_every_frame_and_no_zero_crossing(self):
        for start,end in ((.26,1),(1,3.2),(-.26,-1),(-1,-3.2)):
            for n in range(240):
                x=smooth_path(start,end,n/239)
                self.assertGreater(start*x,0)
                y=value(x)
                self.assertLessEqual(abs(y),4.3)
                self.assertGreaterEqual(abs(y)+1e-10,2)

    def test_geometry_inequalities_for_independent_points(self):
        for k in (.25,1,9):
            for a in (.25,.5,.8,1,1.7,2.4,4):
                for b in (.3,.6,1,1.4,2.4,5):
                    P,Q=branch_points(a,b,k)
                    self.assertAlmostEqual(P[0]*P[1],k)
                    self.assertAlmostEqual(Q[0]*Q[1],k)
                    self.assertGreaterEqual(sum(P)+1e-10,2*math.sqrt(k))
                    self.assertLessEqual(sum(Q)-1e-10,-2*math.sqrt(k))
                    u,v=P[0]-Q[0],P[1]-Q[1]
                    self.assertAlmostEqual(2*(u*u+v*v)-(u+v)**2,(u-v)**2)
                    self.assertGreaterEqual(branch_distance(a,b,k)+1e-10,support_distance(k))

    def test_geometry_animated_paths_and_equality(self):
        states=[(.55,1.8),(2.3,.7),(1.4,2.4),(1,1)]
        for (a,b),(aa,bb) in zip(states,states[1:]):
            for n in range(120):
                t=n/119
                P,Q=branch_points(smooth_path(a,aa,t),smooth_path(b,bb,t))
                self.assertTrue(all(abs(z)<3 for z in (*P,*Q)))
                self.assertGreaterEqual(math.dist(P,Q)+1e-10,2*math.sqrt(2))
        for k in (.25,1,9):
            s=math.sqrt(k);P,Q=branch_points(s,s,k)
            self.assertAlmostEqual(math.dist(P,Q),support_distance(k))
            self.assertAlmostEqual(sum(P),2*math.sqrt(k))
            self.assertAlmostEqual(sum(Q),-2*math.sqrt(k))
            # Normal (1,1) is perpendicular to the support-line direction (1,-1).
            self.assertAlmostEqual((P[0]-Q[0])-(P[1]-Q[1]),0)
        self.assertNotEqual(branch_points(.55,1.8)[0],tuple(-z for z in branch_points(.55,1.8)[1]))

    def test_invalid_inputs(self):
        for args in ((0,1,1),(1,0,1),(1,1,-1)):
            with self.assertRaises(ValueError): value(*args)
        with self.assertRaises(ValueError): branch_points(0,1)
        with self.assertRaises(ValueError): support_distance(-1)


if __name__=='__main__': unittest.main()
