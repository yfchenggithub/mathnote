import math
import unittest
from model import state,from_incentre,projection,sub,dot,norm,mul,add,clip_line


class HyperbolaCentreTests(unittest.TestCase):
    def samples(self):
        for a,b in ((3,4),(2,1),(1,2)):
            for branch in (-1,1):
                for j in range(-40,41):
                    if j: yield state(j/20,branch,a,b)

    def test_hyperbola_branches_and_focal_difference(self):
        for s in self.samples():
            x,y=s['p']; a,b=s['a'],s['b']
            self.assertAlmostEqual(x*x/a**2-y*y/b**2,1)
            self.assertAlmostEqual(s['r1']-s['r2'],2*s['branch']*a)
            self.assertAlmostEqual(s['r1']+s['r2'],2*s['e']*abs(x))
            self.assertAlmostEqual(s['r1'],abs(s['e']*x+a))
            self.assertAlmostEqual(s['r2'],abs(s['e']*x-a))

    def test_centroid_three_medians(self):
        for s in self.samples():
            for vertex,mid in ((s['p'],(0,0)),(s['f1'],s['mid1']),(s['f2'],s['mid2'])):
                expected=add(mul(1/3,vertex),mul(2/3,mid))
                self.assertAlmostEqual(norm(sub(expected,s['g'])),0)

    def test_centroid_coordinate_scale(self):
        for s in self.samples():
            self.assertAlmostEqual(norm(sub(s['g'],mul(1/3,s['p']))),0)
            self.assertAlmostEqual(norm(sub(s['p'],s['g'])),2*norm(s['g']))

    def test_incentre_branch_sign_and_absolute_denominator(self):
        for s in self.samples():
            x,y=s['p']; ix,iy=s['i']; a=s['a']
            self.assertAlmostEqual(ix,s['branch']*a)
            self.assertAlmostEqual(iy,a*y/(a+abs(x)))
            self.assertAlmostEqual(iy,s['c']*y/(s['c']+s['e']*abs(x)))
            self.assertGreater(iy*y,0)

    def test_fixed_base_contact_and_difference(self):
        for s in self.samples():
            self.assertAlmostEqual(s['t'][0],s['branch']*s['a'])
            self.assertAlmostEqual(s['t'][1],0)
            self.assertAlmostEqual(s['i'][0],(s['r1']-s['r2'])/2)
            self.assertAlmostEqual(norm(sub(s['f1'],s['t'])),norm(sub(s['f1'],s['contact1'])))

    def test_real_incircle_tangencies(self):
        for s in self.samples():
            for a,b,foot in ((s['f1'],s['f2'],s['t']),(s['f1'],s['p'],s['contact1']),(s['f2'],s['p'],s['contact2'])):
                self.assertAlmostEqual(norm(sub(s['i'],foot)),s['radius'])
                self.assertAlmostEqual(dot(sub(s['i'],foot),sub(b,a)),0,places=8)
                ratio=dot(sub(foot,a),sub(b,a))/dot(sub(b,a),sub(b,a))
                self.assertGreater(ratio,-1e-10); self.assertLess(ratio,1+1e-10)

    def test_inradius_area_ratio(self):
        for s in self.samples():
            self.assertAlmostEqual(s['radius']*(s['c']+s['e']*abs(s['p'][0])),s['c']*abs(s['p'][1]))
            self.assertAlmostEqual(abs(s['i'][1]/s['p'][1]),s['a']/(s['a']+abs(s['p'][0])))
            self.assertAlmostEqual(s['radius'],abs(s['i'][1]))

    def test_open_locus_all_four_segments(self):
        for s in self.samples():
            self.assertGreater(abs(s['i'][1]),0)
            self.assertLess(abs(s['i'][1]),s['b'])
            expected=s['b']*math.sqrt((abs(s['p'][0])-s['a'])/(abs(s['p'][0])+s['a']))
            self.assertAlmostEqual(abs(s['i'][1]),expected)

    def test_locus_surjectivity_by_inverse(self):
        for branch in (-1,1):
            for t in (-3.99,-2,-.01,.01,2,3.99):
                p=from_incentre(t,branch)
                self.assertAlmostEqual(p[0]**2/9-p[1]**2/16,1,places=7)
                u=math.asinh(p[1]/4); s=state(u,branch)
                self.assertAlmostEqual(s['i'][1],t)
                self.assertAlmostEqual(s['i'][0],branch*3)

    def test_orthocentre_three_altitudes(self):
        for s in self.samples():
            self.assertEqual(s['h'][0],s['p'][0])
            for j,k in ((1,2),(2,1)):
                self.assertAlmostEqual(dot(sub(s['h'],s[f'f{j}']),sub(s['p'],s[f'f{k}'])),0,places=8)

    def test_right_focus_and_two_external_states(self):
        for branch in (-1,1):
            s=state(math.acosh(5/3),branch)
            self.assertAlmostEqual(norm(sub(s['h'],s['f2'] if branch==1 else s['f1'])),0)
        self.assertLess(state(1.22)['h'][1],0)
        s=state(.6)
        self.assertGreater(s['h'][1],s['p'][1])

    def test_altitude_foot_on_side_extension(self):
        for u in (.6,1.22):
            s=state(u); side=sub(s['p'],s['f2']); foot=s['altfoot']
            self.assertAlmostEqual(dot(sub(s['f1'],foot),side),0)
            ratio=dot(sub(foot,s['f2']),side)/dot(side,side)
            self.assertTrue(ratio<0 or ratio>1)

    def test_circumcentre_equal_radii(self):
        for s in self.samples():
            self.assertEqual(s['circum'][0],0)
            for key in ('f1','f2','p'):
                self.assertAlmostEqual(norm(sub(s[key],s['circum'])),s['circumradius'])

    def test_circumcentre_zero_and_sign_change(self):
        u=math.asinh(4/5); s=state(u)
        self.assertAlmostEqual(norm(s['circum']),0)
        self.assertAlmostEqual(dot(sub(s['f1'],s['p']),sub(s['f2'],s['p'])),0)
        self.assertLess(state(.6)['circum'][1],0)
        self.assertGreater(state(1.)['circum'][1],0)

    def test_euler_vector(self):
        for s in self.samples():
            self.assertAlmostEqual(norm(sub(s['h'],sub(mul(3,s['g']),mul(2,s['circum'])))),0,places=8)

    def test_formal_numeric_example(self):
        s=state(math.log(3))
        for key,expected in (('p',(5,16/3)),('g',(5/3,16/9)),('i',(3,2)),('h',(5,0)),('circum',(0,8/3))):
            self.assertAlmostEqual(norm(sub(s[key],expected)),0)

    def test_locus_limits_not_endpoints(self):
        previous=0
        for u in (.1,.5,1,2,3.2):
            y=state(u)['i'][1]
            self.assertGreater(y,previous); self.assertLess(y,4); previous=y
        self.assertAlmostEqual(state(.001)['i'][1],.002,places=7)

    def test_visible_line_clip(self):
        for j in range(60,123):
            s=state(j/100); x,y=s['p']
            for xx,yy in clip_line(x-5,y,-5*(x-5)):
                self.assertAlmostEqual((x-5)*xx+y*yy,-5*(x-5))

    def test_domain(self):
        for branch,a,b,u in ((0,3,4,.5),(1,0,4,.5),(1,3,0,.5),(1,3,4,0)):
            with self.assertRaises(ValueError):state(u,branch,a,b)
        for t in (0,-4,4,5):
            with self.assertRaises(ValueError):from_incentre(t)


if __name__=='__main__':unittest.main()
