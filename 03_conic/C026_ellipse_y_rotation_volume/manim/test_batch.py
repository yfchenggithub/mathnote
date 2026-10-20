import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_rotated_surface_equation(self):
        for t in [i*.1 for i in range(63)]:
            for phi in (0,.3,1.2,3,6):
                x,y,z=profile(t,phi)
                value=x*x/A**2+(y*y+z*z)/B**2 if ROTATION_AXIS=='x' else (x*x+z*z)/A**2+y*y/B**2
                self.assertAlmostEqual(value,1)
    def test_disk_and_integral(self):
        bound=A if ROTATION_AXIS=='x' else B
        for i in range(101):
            q=-bound+2*bound*i/100
            for t in (0,.5,2,4):
                x,y,z=disk(q,t)
                value=x*x/A**2+(y*y+z*z)/B**2 if ROTATION_AXIS=='x' else (x*x+z*z)/A**2+y*y/B**2
                self.assertAlmostEqual(value,1)
        n=1000; dx=2*bound/n
        integral=dx/3*sum(section_area(-bound+i*dx)*(1 if i in (0,n) else 4 if i%2 else 2) for i in range(n+1))
        self.assertAlmostEqual(integral,volume())

if __name__=="__main__": unittest.main()
