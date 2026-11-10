"""Mathematical checks for this UID animation; independent of raster output."""
import math
import numpy as np
import scene_share as s

def test_model():
 for m in np.linspace(math.sqrt(3),2,101):
  roots=s.roots(1,m)
  assert len(roots)==2
  for x in roots:assert abs(x*x/4-(x+m)**2-1)<1e-10
  assert abs(sum(roots)+8*m/3)<1e-10
  assert abs(roots[0]*roots[1]-4*(m*m+1)/3)<1e-10
 assert not s.roots(1,1.4)
 assert s.roots(.5,1)==[-2]
 assert not s.roots(.5,0)
 assert abs(.5*(-2)+1)<1e-12 # one point is vertex; tangent there is vertical, not slope 1/2

if __name__=="__main__":
 test_model();print("C034 mathematics PASS")
