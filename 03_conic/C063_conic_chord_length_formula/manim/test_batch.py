import unittest, math
from model import *

class Tests(unittest.TestCase):
    def test_projection_length(self):
        for i in range(501):
            k=-.8+1.7*i/500;A,B=endpoints(k)
            self.assertAlmostEqual((B[1]-A[1])/(B[0]-A[0]),k)
            self.assertAlmostEqual(length(k),math.sqrt(1+k*k)*abs(A[0]-B[0]))

if __name__=="__main__": unittest.main()
