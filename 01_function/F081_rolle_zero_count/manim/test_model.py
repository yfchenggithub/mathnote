import math,unittest
import model

class F081MathTests(unittest.TestCase):
    def test_equal_endpoints_through_every_morph(self):
        for h in [-1,-.5,0,.5,1]:
            for s in [-.8,0,.4,.75,.8]:
                for u in [0,.1,.5,.9,1]:
                    for x in [-1,1]:self.assertAlmostEqual(model.equal_height(x,h,s,u),1,places=12)
    def test_stationary_is_interior_and_exact(self):
        for i in range(161):
            s=-.8+i*.01;c=model.stationary(s)
            self.assertTrue(-1<c<1)
            for h in [-1,0,1]:self.assertAlmostEqual(model.equal_slope(c,h,s),0,places=12)
            if s:self.assertNotEqual(c,0)
        self.assertAlmostEqual(model.stationary(.75),.75/(1+math.sqrt(2.6875)))
    def test_constant_and_multiwave(self):
        for i in range(201):
            x=-1+i*.01
            self.assertEqual(model.equal_height(x,0,.75),1)
            self.assertEqual(model.equal_slope(x,0,.75),0)
        for c in model.WAVE_STATIONARY:self.assertAlmostEqual(model.equal_slope(c,mixture=1),0,places=12)
    def test_cubic_roots_and_interlacing(self):
        for i in range(241):
            t=-3+i*.025;roots=model.cubic_roots(t)
            self.assertEqual(len(roots),3 if abs(t)<2 else 2 if abs(t)==2 else 1)
            for x in roots:self.assertAlmostEqual(model.cubic(x,t),0,places=10)
            for a,b in zip(roots,roots[1:]):self.assertTrue(any(a<c<b for c in [-1,1]))
        self.assertEqual(model.cubic_roots(2),[-2,1])
        self.assertEqual(model.cubic_roots(-2),[-1,2])
    def test_derivatives_and_visible_plot(self):
        for i in range(161):
            x=-.8+i*.01;h=1e-6
            approx=(model.equal_height(x+h,-1,.75,.3)-model.equal_height(x-h,-1,.75,.3))/(2*h)
            self.assertAlmostEqual(approx,model.equal_slope(x,-1,.75,.3),places=8)
        for t in [0,1,2,3]:
            for segment in model.visible_cubic(t):
                for x,y in segment:
                    self.assertLessEqual(abs(y),5.3)
                    self.assertEqual(y,model.cubic(x,t))

if __name__=='__main__':unittest.main(verbosity=2)
