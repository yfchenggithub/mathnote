import unittest
import numpy as np
from centers_model import *

class CentersTests(unittest.TestCase):
    def test_paths_and_weight_transition(self):
        for start,end in [(GENERAL,EQUILATERAL),(EQUILATERAL,RIGHT_TRIANGLE),(RIGHT_TRIANGLE,GENERAL)]:
            for t in np.linspace(0,1,121):
                A=(1-t)*start+t*end
                V,w,G,I,r=centers(A)
                self.assertGreater(r,0)
                self.assertTrue(np.all(w>0))
                np.testing.assert_allclose(sum(p-G for p in V),0,atol=1e-12)
                for j in range(3):
                    P,Q=V[(j+1)%3],V[(j+2)%3]
                    self.assertAlmostEqual(np.linalg.norm(np.cross(Q-P,I-P))/np.linalg.norm(Q-P),r,places=12)
                    M=(P+Q)/2
                    np.testing.assert_allclose(G,V[j]+2/3*(M-V[j]),atol=1e-12)
                np.testing.assert_allclose(blended_point(A,t),(1-t)*G+t*I,atol=1e-12)
    def test_special_states(self):
        V,w,G,I,r=centers(EQUILATERAL)
        np.testing.assert_allclose(G,I,atol=1e-12)
        np.testing.assert_allclose(w,np.ones(3)/3,atol=1e-12)
        V,w,G,I,r=centers(RIGHT_TRIANGLE)
        self.assertAlmostEqual(np.dot(V[0]-V[1],V[2]-V[1]),0)
        np.testing.assert_allclose(I,[-1.3,.6,0],atol=1e-12)
        np.testing.assert_allclose(G,[-2.6/3,.6,0],atol=1e-12)
        self.assertGreater(np.linalg.norm(G-I),.4)

if __name__=='__main__': unittest.main()
