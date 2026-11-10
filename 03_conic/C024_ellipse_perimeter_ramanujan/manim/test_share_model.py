"""Mathematical checks for this UID animation; independent of raster output."""
import math
import numpy as np
import scene_share as s

def test_model():
 assert abs(s.approx(3,3)-6*math.pi)<1e-12
 assert abs(s.reference(3,3)-6*math.pi)<1e-10
 for b in [3,2,1,.3,.03]:
  r=s.reference(3,b);r2=s.reference(3,b,16384)
  assert abs(r-r2)<1e-8
  assert abs(s.approx(3,b)-r)/r<.000403
 assert abs(s.approx(5,3)-25.5269988628)<1e-8

if __name__=="__main__":
 test_model();print("C024 mathematics PASS")
