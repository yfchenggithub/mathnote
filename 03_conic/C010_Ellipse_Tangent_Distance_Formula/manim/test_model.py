from math import atan2,cos,hypot,pi,sin,sqrt
import unittest
from model import TangentDistanceModel,START,clip_line


class DistanceTests(unittest.TestCase):
    def test_full_sweep_geometry_distances_and_invariants(self):
        for a,b in [(5,4),(5,3),(3,2),(5,4.99)]:
            m=TangentDistanceModel(a,b)
            for i in range(721):
                s=m.state(i*pi/360);u,v=s['normal'];h=s['h'];x,y=s['P']
                self.assertAlmostEqual(x*x/a**2+y*y/b**2,1,places=12)
                self.assertAlmostEqual(u*x+v*y,h,places=12)
                self.assertAlmostEqual(h*h,a*a*u*u+b*b*v*v,places=12)
                self.assertGreater(s['d1'],0);self.assertGreater(s['d2'],0)
                self.assertAlmostEqual(s['d1']*s['d2'],b*b,places=11)
                self.assertAlmostEqual(s['d1']+s['d2'],2*h,places=12)
                self.assertLessEqual(b-1e-12,h);self.assertLessEqual(h,a+1e-12)
                for idx in (1,2):
                    F,H=s['F'+str(idx)],s['H'+str(idx)]
                    self.assertAlmostEqual(u*H[0]+v*H[1],h,places=11)
                    self.assertAlmostEqual((-v)*(H[0]-F[0])+u*(H[1]-F[1]),0,places=11)
                    self.assertAlmostEqual(hypot(H[0]-F[0],H[1]-F[1]),s['d'+str(idx)],places=11)
                    self.assertAlmostEqual(abs(u*F[0]+v*F[1]-h),s['d'+str(idx)],places=11)
                    self.assertAlmostEqual(H[0]**2+H[1]**2,a*a,places=10)
                self.assertAlmostEqual(u*s['Q'][0]+v*s['Q'][1],h,places=12)

    def test_horizontal_vertical_and_distinct_points(self):
        m=TangentDistanceModel()
        s=m.state(pi/2)
        self.assertAlmostEqual(s['d1'],4,places=12);self.assertAlmostEqual(s['d2'],4,places=12)
        self.assertAlmostEqual(s['h'],4,places=12)
        self.assertNotEqual(s['P'],s['H1']);self.assertNotEqual(s['P'],s['H2'])
        s=m.state(0)
        self.assertEqual((s['d1'],s['d2'],s['h']),(8,2,5))
        self.assertEqual(s['P'],s['H1']);self.assertEqual(s['P'],s['H2'])

    def test_formal_non_axis_example(self):
        s=TangentDistanceModel().state(START)
        for actual,target in zip(s['P'],(3,16/5)):
            self.assertAlmostEqual(actual,target,places=12)
        self.assertAlmostEqual(s['d1'],sqrt(34),places=12)
        self.assertAlmostEqual(s['d2'],16/sqrt(34),places=12)
        for actual,target in zip(s['H2'],(75/17,40/17)):
            self.assertAlmostEqual(actual,target,places=12)

    def test_entire_pedal_circle_by_inverse_construction(self):
        m=TangentDistanceModel()
        for i in range(721):
            t=i*pi/360;H=(m.a*cos(t),m.a*sin(t));A,B,D=m.inverse_foot(H)
            self.assertAlmostEqual(D*D,m.a*m.a*A*A+m.b*m.b*B*B,places=10)
            s=m.state(atan2(B,A))
            for actual,target in zip(s['H2'],H):
                self.assertAlmostEqual(actual,target,places=10)

    def test_slope_formula_and_real_line_clipping(self):
        m=TangentDistanceModel()
        for i in range(721):
            s=m.state(i*pi/360);u,v=s['normal'];h=s['h']
            ends=clip_line(u,v,h)
            self.assertEqual(len(ends),2)
            for x,y in ends:
                self.assertAlmostEqual(u*x+v*y,h,places=10)
            if abs(v)>1e-8:
                k=-u/v
                self.assertAlmostEqual(h,sqrt(m.a*m.a*k*k+m.b*m.b)/sqrt(1+k*k),places=11)

    def test_invalid_axes(self):
        for a,b in [(1,1),(1,2),(1,0),(float('inf'),1)]:
            with self.assertRaises(ValueError):
                TangentDistanceModel(a,b)


if __name__=='__main__':
    unittest.main()
