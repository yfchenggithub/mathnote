"""Math gates: all branches, actual trajectory, equality and invalid input."""
import math
import random
import unittest
from model import motion_h, state


class TestConfocal(unittest.TestCase):
    def check_state(self, q):
        a,c,h,x,y=q.a,q.c,q.h,q.x,q.y
        self.assertAlmostEqual(x*x/a**2+y*y/(a*a-c*c),1,places=10)
        self.assertAlmostEqual(x*x/h**2-y*y/(c*c-h*h),1,places=10)
        self.assertAlmostEqual(q.r1+q.r2,2*a,places=10)
        self.assertAlmostEqual(abs(q.r1-q.r2),2*h,places=10)
        self.assertAlmostEqual(q.ellipse_term+q.hyperbola_term,1,places=10)
        self.assertTrue(0<q.theta<math.pi)
        self.assertLessEqual(q.reciprocal_sum,q.upper_bound+1e-9)
        s2=(1-math.cos(q.theta))/2
        t2=1-s2
        self.assertAlmostEqual(1-s2*t2*q.reciprocal_sum**2,
                               (s2/q.e1-t2/q.e2)**2,places=10)

    def test_actual_animation_every_render_frame(self):
        for i in range(24*24+1):
            self.check_state(state(motion_h(i/24)))

    def test_all_branches_and_parameter_ranges(self):
        rng=random.Random(90)
        for _ in range(250):
            c=rng.uniform(.5,4)
            a=c*rng.uniform(1.05,5)
            h=c*rng.uniform(.05,.95)
            angles=[]
            for sx,sy in ((1,1),(1,-1),(-1,1),(-1,-1)):
                q=state(h,c=c,a=a,sx=sx,sy=sy)
                self.check_state(q)
                angles.append(q.theta)
            self.assertLess(max(angles)-min(angles),1e-10)

    def test_exact_final_state(self):
        q=state(1)
        self.assertEqual((q.x,q.y,q.r1,q.r2,q.e1,q.e2),(2,3,5,3,.5,2))
        self.assertAlmostEqual(math.cos(q.theta),3/5)
        self.assertAlmostEqual(q.reciprocal_sum,2.5)
        self.assertAlmostEqual(q.upper_bound,2.5)

    def test_obtuse_and_right_angles_strict(self):
        for theta in (math.pi/2,2*math.pi/3):
            e1=(1+math.sin(theta/2))/2
            e2=math.cos(theta/2)/math.sqrt(1-math.sin(theta/2)**2/e1**2)
            q=state(2/e2,c=2,a=2/e1)
            self.assertAlmostEqual(q.theta,theta)
            self.assertLess(q.reciprocal_sum,q.upper_bound)

    def test_invalid_and_loop(self):
        for h in (0,2,3,-1):
            with self.assertRaises(ValueError): state(h)
        self.assertEqual(motion_h(0),motion_h(24))


if __name__ == '__main__':
    unittest.main()
