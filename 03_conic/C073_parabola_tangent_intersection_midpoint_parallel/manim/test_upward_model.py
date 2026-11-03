import unittest
from model import UpwardConfiguration


class UpwardTests(unittest.TestCase):
    def test_general_geometry(self):
        for p in (-3,-1,1,2,3):
            for a in (-3,-2,0,1,4):
                for b in (-4,-1,0,2,4):
                    if a==b: continue
                    c=UpwardConfiguration(p,a,b)
                    mx,my=c.M; nx,ny=c.N
                    for x,y in (c.A,c.B):
                        self.assertAlmostEqual(x*x,2*p*y)
                        self.assertAlmostEqual(x*mx,p*(my+y))
                    self.assertAlmostEqual(nx,(a+b)/2)
                    self.assertAlmostEqual(ny,(c.A[1]+c.B[1])/2)
                    self.assertAlmostEqual(mx,nx)
                    self.assertAlmostEqual(ny-my,(a-b)**2/(4*p))
                    self.assertNotEqual(c.M,c.N)

    def test_every_motion_sample(self):
        for i in range(961):
            b=3*i/960
            c=UpwardConfiguration(2,-2,b)
            for x0 in (-2,b):
                for x,y in c.tangent_segment(x0):
                    self.assertAlmostEqual(x0*x,2*(y+x0*x0/4))
                    self.assertTrue(-3.000001<=x<=3.500001)
                    self.assertTrue(-2.200001<=y<=3.800001)
            self.assertEqual(c.M[0],c.N[0])
            self.assertGreater(c.N[1],c.M[1])

    def test_critical_states(self):
        c=UpwardConfiguration(2,-2,2)
        self.assertEqual(c.M,(0,-1)); self.assertEqual(c.N,(0,1))
        c=UpwardConfiguration(2,-2,0)
        self.assertEqual(c.M,(-1,0)); self.assertEqual(c.N,(-1,.5))
        self.assertTrue(all(y==0 for x,y in c.tangent_segment(0)))


if __name__=='__main__': unittest.main()
