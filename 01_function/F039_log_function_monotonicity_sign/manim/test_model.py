import unittest,math
from model import log_value,level_intersection,paired_bases,parameter_example

class F039ModelTests(unittest.TestCase):
    def test_domain_fixed_point_and_range(self):
        for a in [.25,1/3,.5,2,3,4]:
            self.assertEqual(log_value(a,1),0)
            for y in [-6,-2,-1,0,.5,1,2,6]:
                self.assertAlmostEqual(log_value(a,a**y),y)
        for a,x in [(1,2),(0,2),(-2,2),(2,0),(2,-1)]:
            with self.assertRaises(ValueError):log_value(a,x)

    def test_monotonicity_and_symmetries(self):
        for a in [.25,1/3,.5,2,3,4]:
            for x1,x2 in [(.125,.25),(.3,.7),(1,2),(3,5)]:
                self.assertEqual(log_value(a,x1)<log_value(a,x2),a>1)
                self.assertAlmostEqual(log_value(a,x1),-log_value(1/a,x1))
            for t in [-2,-1,0,.5,1,2]:self.assertAlmostEqual(log_value(a,a**t),t)

    def test_horizontal_motion_and_visible_curves(self):
        prev=None
        for i in range(401):
            large=2+i/200;a,b=paired_bases(large)
            self.assertAlmostEqual(level_intersection(a,1),large)
            self.assertAlmostEqual(level_intersection(b,-1),large)
            self.assertAlmostEqual(log_value(a,large),1)
            self.assertAlmostEqual(log_value(b,large),-1)
            if prev:self.assertGreater(a,prev[0]);self.assertLess(b,prev[1])
            prev=a,b
            for j in range(51):
                x=.12+(5.2-.12)*j/50
                self.assertLess(abs(log_value(a,x)),3.2)
                self.assertAlmostEqual(log_value(a,x),-log_value(b,x))

    def test_all_existing_examples(self):
        for a in [.5,2,3]:self.assertEqual(log_value(a,2-1),0)
        self.assertLess(log_value(2,3),log_value(2,5))
        self.assertGreater(log_value(.5,3),log_value(.5,5))
        for a in [.3,.5,2,3]:self.assertEqual(log_value(a,2)>log_value(a,3),a<1)
        for a in [.5,2]:
            for x in [-2,0,.5,.6,1,2.9,3,3.1,5]:
                expected=None if x<=.5 else (x>3 if a>1 else x<3)
                self.assertEqual(parameter_example(a,x),expected)
        self.assertLess(log_value(3,2),1)
        self.assertGreater(log_value(2,3),1)
        self.assertEqual(log_value(.5,4),-2)

    def test_added_parameter_and_asymptote(self):
        for a in [-2,-1,0,1,1.1,1.9,2,2.1,4]:
            valid=(a-1>0 and a-1!=1 and a+1>0)
            self.assertEqual(valid,a>1 and a!=2)
        self.assertAlmostEqual(log_value(2,1/8),-3)
        self.assertAlmostEqual(log_value(2,1/2),-1)

if __name__=='__main__':unittest.main()
