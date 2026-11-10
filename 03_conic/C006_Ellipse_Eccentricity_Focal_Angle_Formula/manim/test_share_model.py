"""Mathematical checks for this UID animation; independent of raster output."""
import math
import numpy as np
import scene_share as s

def test_model():
 for t in np.linspace(.001,2*math.pi-.001,721):
  p,h,theta=s.state(t)
  assert abs(p[0]**2/9+p[1]**2/4-1)<1e-12
  assert abs(math.tan(theta/2)-math.sqrt(5)*h/4)<1e-9
  assert math.sin(theta/2)<=math.sqrt(5)/3+1e-12
 assert abs(math.sin(s.state(math.pi/2)[2]/2)-math.sqrt(5)/3)<1e-12
 assert abs(s.state(math.pi/2)[2]-s.state(1.5*math.pi)[2])<1e-12

if __name__=="__main__":
 test_model();print("C006 mathematics PASS")
