"""Mathematical checks for this UID animation; independent of raster output."""
import math
import numpy as np
import scene_share as s

def test_model():
 assert s.intersections(-1)==[]
 for x in np.linspace(0,2.25,201):
  roots=s.intersections(x)
  for a,b in roots:assert abs(b*b-4*a)<1e-12
  assert abs(roots[0][1]+roots[1][1])<1e-12
  assert abs(roots[0][1]*roots[1][1]+4*x)<1e-12
 assert s.intersections(0)==[(0,0),(0,0)]
 assert s.intersections(1)==[(1,2),(1,-2)]

if __name__=="__main__":
 test_model();print("C035 mathematics PASS")
