import math
import unittest
from model import state,project,dot,sub,norm,mul,add,clip_line


class CentreTests(unittest.TestCase):
    def samples(self):
        for a,b in ((5,4),(5,3),(3,2)):
            for i in range(360):
                yield state((i+.5)*math.pi/180,a,b)

    def test_ellipse_and_focal_lengths(self):
        for s in self.samples():
            x,y=s['p']; a,b,c=s['a'],s['b'],s['c']
            self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
            self.assertAlmostEqual(s['r1']+s['r2'],2*a)
            self.assertAlmostEqual(s['r1']-s['r2'],2*c*x/a)

    def test_centroid_medians(self):
        for s in self.samples():
            g=s['g']
            for vertex,midpoint in ((s['p'],(0,0)),(s['f1'],s['midpoint1']),(s['f2'],s['midpoint2'])):
                expected=add(mul(1/3,vertex),mul(2/3,midpoint))
                self.assertAlmostEqual(norm(sub(g,expected)),0)
            self.assertAlmostEqual(norm(sub(g,mul(1/3,s['p']))),0)

    def test_centroid_locus_and_ratio(self):
        for s in self.samples():
            x,y=s['g']; a,b=s['a'],s['b']
            self.assertAlmostEqual(x*x/(a*a/9)+y*y/(b*b/9),1)
            self.assertAlmostEqual(norm(sub(s['p'],s['g'])),2*norm(s['g']))

    def test_incentre_formula_independent_weights(self):
        for s in self.samples():
            x,y=s['p']; ix,iy=s['i']
            self.assertAlmostEqual(ix,s['e']*x)
            self.assertAlmostEqual(iy,s['c']*y/(s['a']+s['c']))
            self.assertGreater(iy*y,0)

    def test_incircle_tangent_to_three_segments(self):
        for s in self.samples():
            for a,b,foot in ((s['f1'],s['f2'],s['t']),(s['f1'],s['p'],s['u']),(s['f2'],s['p'],s['v'])):
                self.assertAlmostEqual(norm(sub(s['i'],foot)),s['radius'])
                self.assertAlmostEqual(dot(sub(s['i'],foot),sub(b,a)),0)
                parameter=dot(sub(foot,a),sub(b,a))/dot(sub(b,a),sub(b,a))
                self.assertGreater(parameter,-1e-10)
                self.assertLess(parameter,1+1e-10)

    def test_incircle_area_and_tangent_difference(self):
        for s in self.samples():
            self.assertAlmostEqual(s['radius']*(s['a']+s['c']),s['area'])
            self.assertAlmostEqual(s['radius'],abs(s['i'][1]))
            self.assertAlmostEqual(s['t'][0],(s['r1']-s['r2'])/2)
            self.assertAlmostEqual(norm(sub(s['f1'],s['t'])),norm(sub(s['f1'],s['u'])))
            self.assertAlmostEqual(norm(sub(s['f2'],s['t'])),norm(sub(s['f2'],s['v'])))

    def test_incentre_locus(self):
        for s in self.samples():
            x,y=s['i']; c=s['c']; by=s['b']*c/(s['a']+c)
            self.assertAlmostEqual(x*x/c**2+y*y/by**2,1)

    def test_orthocentre_all_altitudes(self):
        for s in self.samples():
            h=s['h']
            self.assertAlmostEqual(h[0],s['p'][0])
            self.assertAlmostEqual(dot(sub(h,s['f1']),sub(s['p'],s['f2'])),0,places=8)
            self.assertAlmostEqual(dot(sub(h,s['f2']),sub(s['p'],s['f1'])),0,places=8)
            self.assertAlmostEqual(dot(sub(s['f1'],s['altfoot']),sub(s['p'],s['f2'])),0,places=8)

    def test_right_focus_and_external_orthocentre(self):
        s=state(math.acos(3/5))
        self.assertAlmostEqual(norm(sub(s['h'],s['f2'])),0)
        s=state(math.acos(-3/5))
        self.assertAlmostEqual(norm(sub(s['h'],s['f1'])),0)
        s=state(math.acos(4/5))
        self.assertAlmostEqual(s['h'][0],4)
        self.assertAlmostEqual(s['h'][1],-35/12)

    def test_circumcentre_three_equal_radii(self):
        for s in self.samples():
            self.assertEqual(s['circum'][0],0)
            for vertex in (s['p'],s['f1'],s['f2']):
                self.assertAlmostEqual(norm(sub(vertex,s['circum'])),s['circumradius'])

    def test_circumcentre_crossing_and_obtuse(self):
        s=state(math.acos(math.sqrt(7)/4),5,3)
        self.assertAlmostEqual(norm(s['circum']),0)
        self.assertAlmostEqual(dot(sub(s['f1'],s['p']),sub(s['f2'],s['p'])),0)
        s=state(math.pi/2,5,3)
        self.assertAlmostEqual(s['circum'][1],-7/6)
        self.assertLess(dot(sub(s['f1'],s['p']),sub(s['f2'],s['p'])),0)

    def test_euler_vector(self):
        for s in self.samples():
            expected=sub(mul(3,s['g']),mul(2,s['circum']))
            self.assertAlmostEqual(norm(sub(expected,s['h'])),0,places=8)

    def test_formal_numeric_example(self):
        s=state(math.acos(3/5))
        for key,expected in (('g',(1,16/15)),('i',(9/5,6/5)),('h',(3,0)),('circum',(0,8/5))):
            self.assertAlmostEqual(norm(sub(s[key],expected)),0)

    def test_equilateral_and_isosceles_distinction(self):
        s=state(math.pi/2,2,math.sqrt(3))
        for key in ('i','h','circum'): self.assertAlmostEqual(norm(sub(s[key],s['g'])),0)
        s=state(math.pi/2)
        for key in ('i','h','circum'): self.assertGreater(norm(sub(s[key],s['g'])),.1)

    def test_near_degenerate_limits(self):
        previous=0
        for deg in (3,1,.3):
            s=state(deg*math.pi/180)
            self.assertGreater(abs(s['circum'][1]),previous)
            previous=abs(s['circum'][1])
            self.assertLess(s['radius'],.2)

    def test_line_clipping(self):
        for deg in range(35,146):
            s=state(deg*math.pi/180); x,y=s['p']; c=s['c']
            for xx,yy in clip_line(x-c,y,-c*(x-c)):
                self.assertAlmostEqual((x-c)*xx+y*yy,-c*(x-c))

    def test_domain(self):
        for angle in (0,math.pi,2*math.pi):
            with self.assertRaises(ValueError): state(angle)
        for a,b in ((1,1),(1,2),(2,0)):
            with self.assertRaises(ValueError): state(.5,a,b)


if __name__=='__main__': unittest.main()
