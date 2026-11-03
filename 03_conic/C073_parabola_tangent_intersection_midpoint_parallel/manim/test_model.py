import unittest
from model import Configuration


class ModelTests(unittest.TestCase):
    def test_geometry_sweep(self):
        for p in (-3,-1,1,2,3):
            for a in (-3,-2,0,1,4):
                for b in (-4,-1,0,2,4):
                    if a==b: continue
                    c=Configuration(p,a,b)
                    mx,my=c.M; nx,ny=c.N
                    for x,y in (c.A,c.B):
                        self.assertAlmostEqual(y*y,2*p*x)
                        self.assertAlmostEqual(y*my,p*(mx+x))
                    self.assertAlmostEqual(nx,(c.A[0]+c.B[0])/2)
                    self.assertAlmostEqual(my,ny)
                    self.assertAlmostEqual(nx-mx,(a-b)**2/(4*p))
                    self.assertNotEqual(c.M,c.N)

    def test_every_motion_sample_and_clipped_tangent(self):
        for i in range(961):
            b=4*i/960
            c=Configuration(2,-2,b)
            for y0 in (-2,b):
                for x,y in c.tangent_segment(y0):
                    self.assertAlmostEqual(y0*y,2*(x+y0*y0/4))
                    self.assertTrue(-2.500001<=x<=5.000001)
                    self.assertTrue(-2.650001<=y<=4.650001)
            self.assertTrue(c.M[0]<c.N[0])
            self.assertAlmostEqual(c.M[1],c.N[1])

    def test_critical_states(self):
        c=Configuration(2,-2,2)
        self.assertEqual(c.M,(-1,0)); self.assertEqual(c.N,(1,0))
        c=Configuration(2,-2,0)
        self.assertEqual(c.M,(0,-1)); self.assertEqual(c.N,(.5,-1))
        self.assertEqual(c.tangent_segment(0),((0,-2.65),(0,4.65)))

    def test_invalid_parameters(self):
        for args in ((0,1,2),(2,1,1)):
            with self.assertRaises(ValueError): Configuration(*args)


if __name__=='__main__': unittest.main()
