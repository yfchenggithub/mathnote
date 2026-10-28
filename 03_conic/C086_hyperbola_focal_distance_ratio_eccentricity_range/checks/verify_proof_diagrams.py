from pathlib import Path
from fractions import Fraction as Q
import math,json,re,hashlib
r=Path(__file__).resolve().parents[3];u=r/'03_conic/C086_hyperbola_focal_distance_ratio_eccentricity_range'
checks=0;cases=0
def eq(x,y):
 global checks
 assert math.isclose(float(x),float(y),rel_tol=2e-8,abs_tol=2e-8),(x,y)
 checks+=1
for a in [.5,1,2,4]:
 for lam in [.2,.5,.75,1.25,1.5,2,3,5]:
  K=(1+lam)/abs(1-lam)
  for q in [.1,.4,.75,1,1.3]:
   cases+=1;e=1+(K-1)*q;c=e*a;b=a*math.sqrt(e*e-1)
   r2=2*a/abs(lam-1);r1=lam*r2;x=(r1*r1-r2*r2)/(4*c)
   y2=r1*r1-(x+c)**2
   eq(abs(r1-r2),2*a);eq((r1+r2)/abs(r1-r2),K)
   eq(x,a/e*(1+lam)/(lam-1))
   allowed=e<=K+1e-10
   assert allowed==(abs(x)>=a-1e-10)==(2*c<=r1+r2+1e-10)
   if allowed:
    assert y2>=-1e-8;y=math.sqrt(max(0,y2))
    eq(x*x/a**2-y*y/b**2,1)
    for yy in [y,-y]:
     eq(math.hypot(x+c,yy),r1);eq(math.hypot(x-c,yy),r2)
    eq(r1/r2,lam)
    assert (x>0)==(lam>1)
    if q==1:eq(y2,0);eq(abs(x),a)
    else:assert y>0
   else:assert y2<0
# Fixed e: branch ratio endpoints and finite points never attaining 1.
for e in [1.25,1.5,2,3,5]:
 for a in [1,2]:
  b=a*math.sqrt(e*e-1);c=e*a
  for sign in [-1,1]:
   for xx in [1,1.1,2,10,1000]:
    x=sign*a*xx;y=b*math.sqrt(xx*xx-1)
    d1=math.hypot(x+c,y);d2=math.hypot(x-c,y);lam=d1/d2
    eq(abs(d1-d2),2*a);assert lam!=1
    assert (e-1)/(e+1)-1e-10<=lam<1 if sign<0 else 1<lam<=(e+1)/(e-1)+1e-10
    if xx==1:eq(lam,(e+sign)/(e-sign))
# Exact standard example and all eight example answers.
assert Q(3)**2/4-Q(15)/12==1
assert Q(7)**2+Q(15)==64 and Q(-1)**2+Q(15)==16
assert (1+Q(2))/abs(1-Q(2))==3 and (1+Q(1,2))/abs(1-Q(1,2))==3
assert (Q(2)-1)/(Q(2)+1)==Q(1,3) and (Q(2)+1)/(Q(2)-1)==3
assert (1+Q(3))/(Q(3)-1)==2
for c,expected in [(2,2),(3,1),(Q(7,2),0)]:
 r1,r2=Q(4),Q(2);x=(r1*r1-r2*r2)/(4*c);y2=r1*r1-(x+c)**2
 assert (2 if y2>0 else 1 if y2==0 else 0)==expected
# Elementary rods, triangle length bars, vertex rows, and circle diagram.
for d in [4,6]:
 x=6/d;y=math.sqrt(max(0,16-(x+d/2)**2))
 eq(math.hypot(x+d/2,y),4);eq(math.hypot(x-d/2,y),2)
eq(4*.95,7-3.2);eq(2*.95,8.9-7);eq(2*.95,5.1-3.2)
for vertex in [-1,1]:eq(abs(vertex+3)+abs(vertex-3),6)
for yy in [0,2,5]:eq(math.hypot(4,yy),math.hypot(-4,yy))

# Ratio-circle and extrema checks, independent of the hyperbola model.
circle_points=0
for c in [1.5,2,3,4]:
 for lam in [.2,.5,.8,1.2,2,3,5]:
  h=c*(lam*lam+1)/(lam*lam-1);R=2*c*lam/abs(lam*lam-1)
  for deg in range(0,360,15):
   P=(h+R*math.cos(math.radians(deg)),R*math.sin(math.radians(deg)))
   eq(math.hypot(P[0]+c,P[1])/math.hypot(P[0]-c,P[1]),lam);circle_points+=1
  if lam>1:
   d=h-c
   assert R>d>0
   eq(R-d,2*c/(lam+1));eq(R+d,2*c/(lam-1))
   eq((lam-1)*(R+d),2*c)
   eq((lam-1)*(R-d),2*c*(lam-1)/(lam+1))
eq((6.1-4.7)/.525,Q(8,3));eq((10.3-6.1)/.525,8)
eq(Q(20,3)-Q(16,3),Q(4,3))
eq((Q(3)-Q(20,3))**2+15,Q(16,3)**2)
eq(Q(3)*(Q(2)-1)/(Q(2)+1),1)
assert '方法五：两焦点作圆心' in (r/'assets/tikz/C086_circle_proof.tex').read_text(encoding='utf8')
proof=(u/'03_proof.tex').read_text(encoding='utf8')
sections=re.split(r'\\textbf\{方法[一二三四五]：',proof)[1:]
assert len(sections)==5
expected=['C086_triangle_proof','C086_parts_proof','C086_coordinate_proof','C086_apollonius_extrema','C086_circle_proof']
for section,figure in zip(sections,expected):
 assert 'assets/tikz/'+figure in section
 assert (r/'assets/tikz'/f'{figure}.tex').is_file()
assert all(f'例{i}（' in (u/'04_examples.tex').read_text(encoding='utf8') for i in range(1,10))
meta=json.loads((u/'meta.json').read_text(encoding='utf8'))
assert meta['id']=='C086' and meta['meta']['updated_at']=='2026-10-28'
print(json.dumps(dict(status='PASS',existence_cases=cases,equalities=checks,
 ratio_circle_samples=circle_points,proof_methods_with_diagrams=5,examples_preserved=9),indent=2))
