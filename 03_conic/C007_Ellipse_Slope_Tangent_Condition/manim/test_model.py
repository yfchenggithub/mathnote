from math import cos,pi,sin
import unittest
from model import SlopeTangentModel,clip_line


class TangencyTests(unittest.TestCase):
    def test_intersection_roots_and_discriminant(self):
        for a,b in [(3,2),(2,1),(4,3.9)]:
            for k in (-2,-.5,0,.5,2):
                model=SlopeTangentModel(a,b,k)
                for ratio in (-1.3,-1,-.9,0,.9,1,1.3):
                    m=ratio*model.critical
                    roots=model.intersections(m)
                    expected=1 if abs(ratio)==1 else 2 if abs(ratio)<1 else 0
                    self.assertEqual(len(roots),expected)
                    A=b*b+a*a*k*k; B=2*a*a*k*m; C=a*a*(m*m-b*b)
                    self.assertAlmostEqual(B*B-4*A*C,4*a*a*b*b*(model.S-m*m),places=8)
                    for x,y in roots:
                        self.assertAlmostEqual(x*x/a**2+y*y/b**2,1,places=11)
                        self.assertAlmostEqual(y,k*x+m,places=12)

    def test_tangent_coordinates_and_true_tangent_direction(self):
        for k in (-3,-.5,0,.5,3):
            model=SlopeTangentModel(k=k)
            for sign in (-1,1):
                m,(x,y)=model.tangent(sign)
                self.assertEqual(model.count(m),1)
                self.assertAlmostEqual(x*x/model.a**2+y*y/model.b**2,1,places=12)
                self.assertAlmostEqual(y,k*x+m,places=12)
                # Ellipse normal is orthogonal to direction (1,k).
                self.assertAlmostEqual(x/model.a**2+k*y/model.b**2,0,places=12)

    def test_formal_example_and_central_symmetry(self):
        model=SlopeTangentModel()
        self.assertEqual(model.S,6.25)
        self.assertEqual([model.count(m) for m in (2,2.5,3)],[2,1,0])
        for sign in (-1,1):
            m,(x,y)=model.tangent(sign)
            self.assertAlmostEqual(x,-sign*1.8,places=12)
            self.assertAlmostEqual(y,sign*1.6,places=12)
        for m in (-3,-2.5,-2,0,2,2.5,3):
            reflected=sorted((-x,-y) for x,y in model.intersections(m))
            actual=sorted(model.intersections(-m))
            for first,second in zip(reflected,actual):
                for u,v in zip(first,second):
                    self.assertAlmostEqual(u,v,places=12)

    def test_support_extrema_on_ellipse(self):
        for k in (-2,0,.5,2):
            model=SlopeTangentModel(k=k)
            for i in range(721):
                t=i*pi/360; x=model.a*cos(t); y=model.b*sin(t)
                self.assertLessEqual(abs(y-k*x),model.critical+1e-12)
            for sign in (-1,1):
                m,(x,y)=model.tangent(sign)
                self.assertAlmostEqual(y-k*x,m,places=12)

    def test_general_form_and_vertical_boundary(self):
        model=SlopeTangentModel()
        for m in (-3,-2.5,-2,0,2,2.5,3):
            self.assertEqual(model.count(m),model.general_count(-model.k,1,-m))
        for sign in (-1,1):
            self.assertEqual(model.general_count(1,0,-sign*3),1)
        self.assertEqual(model.general_count(1,0,-2),2)
        self.assertEqual(model.general_count(1,0,-4),0)

    def test_all_storyboard_lines_are_clipped_on_true_line(self):
        for i in range(601):
            m=-3+i*.01
            points=clip_line(.5,m)
            self.assertEqual(len(points),2)
            for x,y in points:
                self.assertAlmostEqual(y,.5*x+m,places=12)
                self.assertLessEqual(abs(x),3.6+1e-12)
                self.assertLessEqual(abs(y),3.05+1e-12)

    def test_invalid_domain(self):
        for a,b,k in [(1,1,0),(1,2,0),(1,0,1),(3,2,float('inf'))]:
            with self.assertRaises(ValueError):
                SlopeTangentModel(a,b,k)
        with self.assertRaises(ValueError):
            SlopeTangentModel().general_count(0,0,1)


if __name__=='__main__':
    unittest.main()
