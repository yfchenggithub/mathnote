import unittest
from model import f,extrema,general_extrema
class ModelTest(unittest.TestCase):
 def test_source_windows(self):
  for m,n,near,mn,mx,far in [(0,4,2,1,5,[0,4]),(3,4,3,2,5,[4]),(0,1,1,2,5,[0])]:
   r=extrema(m,n);self.assertEqual((r['nearest'],r['minimum'],r['maximum'],r['farthest']),(near,mn,mx,far))
 def test_entire_motion(self):
  for endpoints in [(0,4,3,4),(3,4,0,1),(0,1,0,4)]:
   for i in range(201):
    t=i/200;m=endpoints[0]*(1-t)+endpoints[2]*t;n=endpoints[1]*(1-t)+endpoints[3]*t;r=extrema(m,n)
    self.assertLessEqual(m,r['nearest']);self.assertLessEqual(r['nearest'],n)
    for j in range(51):
     y=f(m+(n-m)*j/50);self.assertGreaterEqual(y+1e-10,r['minimum']);self.assertLessEqual(y-1e-10,r['maximum'])
 def test_both_openings_and_boundaries(self):
  for a in [-2,-.5,.5,3]:
   for h in [-2,0,1,2,4,6]:
    mn,mx=general_extrema(a,h,3,0,4)
    for i in range(201):
     y=a*(i/50-h)**2+3;self.assertGreaterEqual(y+1e-10,mn);self.assertLessEqual(y-1e-10,mx)
 def test_invalid(self):
  with self.assertRaises(ValueError):extrema(1,0)
  with self.assertRaises(ValueError):general_extrema(0,1,2,0,4)
if __name__=='__main__':unittest.main()
