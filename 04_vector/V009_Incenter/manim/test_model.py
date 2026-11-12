import unittest
import numpy as np
from model import geometry

class IncenterTests(unittest.TestCase):
    def test_entire_motion(self):
        for t in np.linspace(0,2*np.pi,401):
            V,s,I,F,r = geometry(t)
            self.assertTrue(all(s[i]+s[(i+1)%3]>s[(i+2)%3] for i in range(3)))
            np.testing.assert_allclose(sum(w*(p-I) for w,p in zip(s,V)),0,atol=1e-12)
            areas=[]
            for j,(P,Q) in enumerate([(V[1],V[2]),(V[2],V[0]),(V[0],V[1])]):
                self.assertAlmostEqual(np.linalg.norm(I-F[j]),r,places=12)
                self.assertAlmostEqual(np.dot(I-F[j],Q-P),0,places=12)
                fraction=np.dot(F[j]-P,Q-P)/np.dot(Q-P,Q-P)
                self.assertTrue(0<fraction<1)
                areas.append(abs(np.cross(P-I,Q-I)[2])/2)
            np.testing.assert_allclose(np.array(areas)/s,r/2,atol=1e-12)
            A,B,C=V
            D=(s[1]*B+s[2]*C)/(s[1]+s[2])
            np.testing.assert_allclose(I,A+(s[1]+s[2])/sum(s)*(D-A),atol=1e-12)

if __name__=='__main__': unittest.main()
