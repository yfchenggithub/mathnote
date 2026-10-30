import math
import unittest
from model import state


class C089MathTests(unittest.TestCase):
    def samples(self):
        for a,b in [(1.5,1),(3,2),(.3,4)]:
            for branch in [-1,1]:
                for i in range(601):
                    yield state(-3+i/100,a,b,branch)

    def test_curve_and_both_asymptotes(self):
        for s in self.samples():
            self.assertAlmostEqual((s.p[0]/s.a)**2-(s.p[1]/s.b)**2,1,places=10)
            self.assertAlmostEqual(s.A[1],s.b/s.a*s.A[0],places=10)
            self.assertAlmostEqual(s.B[1],-s.b/s.a*s.B[0],places=10)

    def test_tangent_incidence_and_gradient(self):
        for s in self.samples():
            for q in [s.A,s.B,s.p]:
                self.assertAlmostEqual(s.tangent_residual(q),0,places=10)
            # P'(t) is parallel to the segment AB, also at the vertices.
            dx=s.branch*s.a*math.sinh(s.t); dy=s.branch*s.b*math.cosh(s.t)
            self.assertAlmostEqual(dx*(s.A[1]-s.B[1])-dy*(s.A[0]-s.B[0]),0,places=10)

    def test_midpoint(self):
        for s in self.samples():
            for j in [0,1]:
                self.assertAlmostEqual((s.A[j]+s.B[j])/2,s.p[j],places=10)

    def test_area_length_product_and_angle(self):
        for s in self.samples():
            self.assertAlmostEqual(s.area,s.a*s.b,places=10)
            self.assertAlmostEqual(s.length_product,s.a*s.a+s.b*s.b,places=10)
            sine=2*s.area/s.length_product
            self.assertAlmostEqual(sine,2*s.a*s.b/(s.a*s.a+s.b*s.b),places=10)

    def test_vertices_and_numeric_example(self):
        for sign in [-1,1]:
            s=state(0,3,2,sign)
            self.assertEqual(s.p,(sign*3,0))
            self.assertEqual(s.A,(sign*3,sign*2))
            self.assertEqual(s.B,(sign*3,-sign*2))
            self.assertEqual(s.area,6)
        s=state(math.log(3),3,2)
        for actual,expected in zip((*s.A,*s.B,*s.p),(9,6,1,-2/3,5,8/3)):
            self.assertAlmostEqual(actual,expected)

    def test_displayed_trajectory_stays_inside_graph(self):
        for i in range(1001):
            s=state(-.75+1.5*i/1000)
            for q in [s.A,s.B,s.p]:
                self.assertTrue(0<q[0]<3.2)
                self.assertTrue(-2.2<q[1]<2.2)
            self.assertEqual(f'{s.area:.2f}','1.50')

    def test_invalid_inputs(self):
        for args in [(0,0,1),(0,1,-1),(0,1,1,0),(float('nan'),1,1)]:
            with self.assertRaises(ValueError):
                state(*args)


if __name__=='__main__':
    unittest.main()
