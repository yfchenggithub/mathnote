import math
import unittest
from model import state,area_maximum,clip_line,beam,dot,sub,length,unit,mul


class GeometryTests(unittest.TestCase):
    def test_support_line_and_tangency(self):
        for a,b in ((3,2),(2,1),(2,math.sqrt(3))):
            for i in range(361):
                s=state(i*math.pi/180,a,b); x,y=s['p']
                self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
                self.assertAlmostEqual(dot(s['n'],s['p']),s['h'])
                self.assertAlmostEqual(s['n'][0]*y/b**2-s['n'][1]*x/a**2,0)

    def test_feet_are_actual_projections(self):
        for i in range(721):
            s=state(i*math.pi/360)
            for j in (1,2):
                f,h=s[f'f{j}'],s[f'h{j}']
                self.assertAlmostEqual(dot(s['n'],h),s['h'])
                self.assertAlmostEqual(length(sub(h,f)),s[f'd{j}'])
                self.assertAlmostEqual(sub(h,f)[0]*s['n'][1]-sub(h,f)[1]*s['n'][0],0)

    def test_distance_product_full_ellipse(self):
        for a,b in ((3,2),(2,1),(2,math.sqrt(3))):
            for i in range(721):
                s=state(i*math.pi/360,a,b)
                self.assertGreater(s['d1'],0); self.assertGreater(s['d2'],0)
                self.assertAlmostEqual(s['d1']*s['d2'],b*b)

    def test_axis_product_anchor(self):
        s=state(0)
        self.assertAlmostEqual(s['d1'],3+math.sqrt(5))
        self.assertAlmostEqual(s['d2'],3-math.sqrt(5))
        self.assertAlmostEqual(length(sub(s['h1'],s['p'])),0)
        self.assertAlmostEqual(length(sub(s['h2'],s['p'])),0)

    def test_auxiliary_circle(self):
        for i in range(721):
            s=state(i*math.pi/360)
            self.assertAlmostEqual(length(s['h1']),3)
            self.assertAlmostEqual(length(s['h2']),3)

    def test_reflection_and_midline(self):
        for i in range(361):
            s=state(i*math.pi/180)
            self.assertAlmostEqual(length(sub(s['q'],s['p'])),s['r1'])
            self.assertAlmostEqual(length(sub(s['q'],s['f2'])),6)
            self.assertAlmostEqual(length(sub(s['q'],s['f2'])),length(sub(s['q'],s['p']))+s['r2'])
            for actual,expected in zip(s['reflected'],unit(sub(s['f2'],s['p']))): self.assertAlmostEqual(actual,expected)

    def test_normal_bisects_internal_angle(self):
        for i in range(1,180):
            s=state(i*math.pi/180)
            v1,v2=unit(sub(s['f1'],s['p'])),unit(sub(s['f2'],s['p']))
            self.assertAlmostEqual(dot(v1,mul(-1,s['n'])),dot(v2,mul(-1,s['n'])))

    def test_beam_propagation(self):
        for phi in (.5,1.1,2):
            s=state(phi)
            self.assertEqual(beam(phi,0),s['f1'])
            self.assertAlmostEqual(length(sub(beam(phi,1),s['f2'])),0)
            self.assertAlmostEqual(length(sub(beam(phi,s['r1']/6),s['p'])),0)
            for p in (.1,.3,.7,.9):
                pos=beam(phi,p)
                if p*6<=s['r1']: self.assertAlmostEqual(length(sub(pos,s['f1'])),p*6)
                else: self.assertAlmostEqual(length(sub(pos,s['p'])),p*6-s['r1'])

    def test_power_chord(self):
        for phi in (.2,.7,1.3,2.1,4.2):
            s=state(phi); k=mul(-1,s['h2']); v=sub(s['h1'],s['f1']); w=sub(k,s['f1'])
            self.assertAlmostEqual(v[0]*w[1]-v[1]*w[0],0)
            self.assertLess(dot(v,w),0)
            self.assertAlmostEqual(length(w),s['d2'])

    def test_intercepts_independently(self):
        for i in range(360):
            phi=(i+.5)*math.pi/180; s=state(phi,2,1)
            nx,ny=s['n']; px,py=s['p']
            self.assertAlmostEqual(nx*s['xn'],s['h'])
            self.assertAlmostEqual((s['xm']-px)*ny-(-py)*nx,0)
            self.assertAlmostEqual(s['xm']*s['xn'],3)

    def test_intercept_exceptions(self):
        for i in (1,3): self.assertIsNone(state(i*math.pi/2)['xn'])
        for i in (0,2): self.assertIsNone(state(i*math.pi/2)['xm'])

    def test_area_projection_identity(self):
        for a,b in ((3,2),(2,1),(2,math.sqrt(3))):
            for i in range(361):
                s=state(i*math.pi/180,a,b); v=s['d1']+s['d2']; u=s['chord']
                self.assertAlmostEqual(s['area'],u*v/2)
                self.assertAlmostEqual(u*u+v*v,4*a*a)
                self.assertAlmostEqual(s['area'],2*s['c']*abs(s['n'][1])*s['h'])

    def test_area_regimes_and_maxima(self):
        for a,b in ((2,math.sqrt(3)),(2,math.sqrt(2)),(2,1),(5,3)):
            bound,phi=area_maximum(a,b)
            self.assertAlmostEqual(state(phi,a,b)['area'],bound)
            for i in range(721): self.assertLessEqual(state(i*math.pi/360,a,b)['area'],bound+1e-9)
        self.assertAlmostEqual(area_maximum(2,math.sqrt(3))[0],2*math.sqrt(3))
        self.assertAlmostEqual(area_maximum(2,1)[0],4)
        self.assertAlmostEqual(area_maximum(2,math.sqrt(2))[0],4)

    def test_area_degeneracy(self):
        for phi in (0,math.pi):
            s=state(phi)
            self.assertAlmostEqual(s['area'],0)
            self.assertAlmostEqual(s['chord'],0)

    def test_clipping(self):
        for i in range(361):
            s=state(i*math.pi/180)
            for p in clip_line(s['n'],s['h']): self.assertAlmostEqual(dot(s['n'],p),s['h'])

    def test_domain(self):
        for a,b in ((1,1),(1,2),(2,0)):
            with self.assertRaises(ValueError): state(.5,a,b)


if __name__=='__main__': unittest.main()
