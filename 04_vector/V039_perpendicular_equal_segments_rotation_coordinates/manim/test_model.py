import unittest
from math import pi
from model import CENTER, SOURCE, rotate, quarter_turn, triangle, displacement, audit_state

class RotationMathTests(unittest.TestCase):
    def test_formal_example(self):
        self.assertEqual(quarter_turn(CENTER,SOURCE,1),(-2,2))
        self.assertEqual(quarter_turn(CENTER,SOURCE,-1),(6,-4))

    def test_both_directions_all_quadrants_and_axis_cases(self):
        for a,b in [(0,0),CENTER,(-3,4)]:
            for u in range(-5,6):
                for v in range(-5,6):
                    if u==v==0: continue
                    p=(a+u,b+v)
                    for direction in (-1,1):
                        q=quarter_turn((a,b),p,direction)
                        s,t=displacement((a,b),q)
                        self.assertEqual(u*s+v*t,0)
                        self.assertEqual(s*s+t*t,u*u+v*v)
                        self.assertEqual(abs(s),abs(v))
                        self.assertEqual(abs(t),abs(u))
                        numerical=rotate((a,b),p,direction*pi/2)
                        for x,y in zip(numerical,q): self.assertAlmostEqual(x,y,places=12)

    def test_continuous_motion_is_rigid_not_endpoint_interpolation(self):
        for j in range(-360,361):
            angle=j*pi/720
            state=audit_state(angle)
            self.assertAlmostEqual(state['length_squared'],25,places=11)
            self.assertAlmostEqual(state['triangle_dot'],0,places=11)
            b,h,r=triangle(angle=angle)
            self.assertEqual(b,CENTER)
            self.assertAlmostEqual(sum(x*x for x in displacement(b,h)),9,places=11)
            self.assertAlmostEqual(sum(x*x for x in displacement(h,r)),16,places=11)
        self.assertNotAlmostEqual(audit_state(pi/4)['source_dot_rotated'],0)

    def test_nonzero_condition_and_direction(self):
        with self.assertRaises(ValueError): quarter_turn(CENTER,CENTER,1)
        with self.assertRaises(ValueError): quarter_turn(CENTER,SOURCE,0)

if __name__=='__main__': unittest.main()
