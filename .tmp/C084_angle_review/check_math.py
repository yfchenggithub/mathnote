from fractions import Fraction as F
from math import cosh,sinh,hypot,isclose,sqrt
from pathlib import Path
import json,hashlib
checks=0
def eq(a,b):
 global checks
 assert isclose(a,b,rel_tol=2e-8,abs_tol=2e-8),(a,b)
 checks+=1
for a,b in [(3,4),(1,1),(2,3)]:
 c=hypot(a,b)
 for sx in [-1,1]:
  for sy in [-1,1]:
   points=[(sx*a*cosh(t),sy*b*sinh(t)) for t in [.01,.4,1,2]]
   points.append((sx*c,sy*b*b/a))
   for x,y in points:
    mi=a*a/x;mo=c*c*x/(a*a)
    assert abs(mi)<a<c<abs(mo)
    eq((y/(x-mi))*(y/(x-mo)),-1)
    for m in [mi,mo,x/3]:
     D1=(x-m)*(x+c)+y*y;D2=(x-m)*(x-c)+y*y
     eq((c+m)*D2-(c-m)*D1,2/a**2*(m*x-a*a)*(c*c*x-a*a*m))
    # determinant / dot version covers vertical focal line as well.
    D1=(x-mi)*(x+c)+y*y;D2=(x-mi)*(x-c)+y*y
    assert D1>0 and D2>0
    eq(y*(c+mi)/D1,y*(c-mi)/D2)
x=F(15,4);y=F(3);c=F(5);mi=F(12,5);mo=F(125,12)
k1=y/(x+c);k2=y/(x-c);ki=y/(x-mi);ko=y/(x-mo)
assert ki==F(20,9) and ko==F(-9,20)
assert (ki-k1)/(1+ki*k1)==(k2-ki)/(1+k2*ki)==F(16,15)
assert (ko-k1)/(1+ko*k1)==(k2-ko)/(1+k2*ko)==F(-15,16)
r=Path('D:/mathnote');u=r/'03_conic/C084_hyperbola_focal_triangle_internal_angle_bisector';w=r/'.tmp/C084_angle_review'
assert hashlib.sha256((u/'pdfs/C084_hyperbola_focal_triangle_internal_angle_bisector.pdf').read_bytes()).hexdigest()==(w/'formal_pdf.sha256').read_text()
for p in (w/'before').iterdir():
 if p.name not in ['03_proof.tex','meta.json']:assert p.read_bytes()==(u/p.name).read_bytes(),p.name
print(json.dumps({'status':'PASS','cases':60,'numeric_equalities':checks,'exact_example':'in=12/5, out=125/12; slopes=20/9,-9/20; tangent quotients=16/15,-15/16','vertical_cases':'x=+/-c included','preserved':'other six-part files, main/source and formal PDF'},indent=2))
