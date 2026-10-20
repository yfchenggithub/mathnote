import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_polygon_area(self):
        for a,b in ((1,1),(3,2),(2.4,2.5),(2,3)):
            pts=[point(i*2*math.pi/2000,a,b) for i in range(2000)]
            shoelace=abs(sum(pts[i][0]*pts[(i+1)%2000][1]-pts[(i+1)%2000][0]*pts[i][1] for i in range(2000)))/2
            self.assertAlmostEqual(shoelace,area(a,b),delta=4e-5)
            for x,y in pts[::20]: self.assertAlmostEqual(x*x/a**2+y*y/b**2,1)
    def test_constant_product(self):
        for i in range(101):
            a=2.4+i*.006
            self.assertAlmostEqual(area(a,6/a),6*math.pi)

if __name__=="__main__": unittest.main()
