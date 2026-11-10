"""Mathematical checks for this UID animation; independent of raster output."""
import math
import numpy as np
import scene_share as s

def test_model():
 for t in np.linspace(0,2*math.pi,721):
  p,f,r1,r2,d=s.state(t);n=p/np.array([9,4]);v=np.array([-n[1],n[0]])
  assert abs(p[0]**2/9+p[1]**2/4-1)<1e-12
  assert abs(np.dot(n,p)-1)<1e-12 and abs(np.dot(n,f)-1)<1e-12
  assert abs(np.dot(f,v))<1e-12
  assert abs(r1+r2-6)<1e-12 and abs(math.sqrt(r1*r2)*d-6)<1e-12

if __name__=="__main__":
 test_model();print("C021 mathematics PASS")
