"""Mathematical checks for this UID animation; independent of raster output."""
import math
import numpy as np
import scene_share as s

def test_model():
 for m in np.linspace(-2.5,2.5,201):
  roots=s.roots(m)
  assert len(roots)==2
  for x in roots:
   y=.5*x+m
   assert abs(x*x/9+y*y/4-1)<1e-10
  assert abs(sum(roots)+36*m/25)<1e-10
  assert abs(roots[0]*roots[1]-36*(m*m-4)/25)<1e-10
 assert abs(s.roots(2.5)[0]-s.roots(2.5)[1])<1e-10
 assert not s.roots(2.9)

if __name__=="__main__":
 test_model();print("C033 mathematics PASS")
