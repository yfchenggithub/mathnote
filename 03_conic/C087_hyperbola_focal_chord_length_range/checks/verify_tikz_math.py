"""Independent C087 checks: actual coordinates, formulas, ranges and proof coverage."""
from pathlib import Path
from fractions import Fraction as Q
from math import sqrt,hypot,isclose,cos,radians
import json,re
ROOT=Path(__file__).resolve().parents[3]
UID=ROOT/'03_conic/C087_hyperbola_focal_chord_length_range'
checks=0
def eq(x,y):
    global checks
    assert isclose(float(x),float(y),rel_tol=2e-7,abs_tol=2e-7),(x,y)
    checks+=1
def point(P,a=3,b=4):eq(P[0]**2/a**2-P[1]**2/b**2,1)
def length(a,b,k):return 2*a*b*b*(1+k*k)/abs(a*a*k*k-b*b)
cases=0
for a,b in [(1,1),(3,4),(4,2),(2,5)]:
 c=hypot(a,b)
 for factor in [0,.1,-.1,.5,-.5,.99,-.99,1.01,-1.01,2,-2,10,-10]:
  k=factor*b/a;s=sqrt(1+k*k)
  ts=[-b*b/(c+a*s),-b*b/(c-a*s)]
  ps=[(c+t,k*t) for t in ts]
  for P,t in zip(ps,ts):
   point(P,a,b)
   eq((b*b-a*a*k*k)*t*t+2*c*b*b*t+b**4,0)
  L=hypot(ps[0][0]-ps[1][0],ps[0][1]-ps[1][1])
  eq(L,length(a,b,k));eq(L,2*a*b*b/abs(a*a-c*c/(1+k*k)))
  eq(ts[0]*ts[1],b**4/(b*b-a*a*k*k))
  assert ps[0][0]>=a-1e-8
  if abs(factor)<1:
   assert ps[1][0]<=-a+1e-8
   eq(L-2*a,2*a*c*c*k*k/(b*b-a*a*k*k))
   assert L>=2*a-1e-8
  else:
   assert ps[1][0]>c
   eq(L-2*b*b/a,2*b*b*c*c/(a*(a*a*k*k-b*b)))
   assert L>2*b*b/a
  cases+=1
 # Vertical and excluded slopes need independent substitution, not a k=infinity value.
 for sign in [-1,1]:point((c,sign*b*b/a),a,b)
 eq(2*b*b/a,2*a*b*b/(a*a))
 t=-b*b/(2*c)
 for k in [-b/a,b/a]:point((c+t,k*t),a,b)
 # Inverse-length ranges cover each full interval.
 for L in [2*a,2*a+1,2*a+20]:
  u=b*b*(L-2*a)/(a*a*L+2*a*b*b)
  assert 0<=u<b*b/a**2;eq(length(a,b,sqrt(u)),L)
 for L in [2*b*b/a+1,2*b*b/a+20]:
  u=b*b*(L+2*a)/(a*a*L-2*a*b*b)
  assert u>b*b/a**2;eq(length(a,b,sqrt(u)),L)

# Read the actual explicit TikZ coordinates used in the four proof diagrams.
for name in ['root_projection','vertical_parameter','focal_triangle','opposite_rays']:
 text=(ROOT/f'assets/tikz/C087_{name}.tex').read_text(encoding='utf8')
 m={key:(float(x),float(y)) for key,x,y in re.findall(r'\\coordinate \((\w+)\) at \(([-\d.]+),([-\d.]+)\);',text)}
 for key in ['A','B','P']:
  if key in m:point(m[key])
 if name=='root_projection':
  A,B,H,F=m['A'],m['B'],m['H'],m['F']
  eq(H[0],B[0]);eq(H[1],A[1])
  for P in [A,B]:eq(P[1],Q(5,12)*(P[0]-5))
  eq(hypot(A[0]-B[0],A[1]-B[1]),sqrt(1+(5/12)**2)*abs(A[0]-B[0]))
 if name=='vertical_parameter':
  eq(m['A'][0],5);eq(m['B'][0],5)
  eq(m['A'][1]-m['B'][1],Q(32,3))
 if name=='focal_triangle':
  P,F1,F2=m['P'],m['Fone'],m['Ftwo']
  r=hypot(P[0]-5,P[1]);eq(r,8)
  eq(hypot(P[0]+5,P[1]),14)
  eq((P[0]-5)/r,.2);eq(cos(radians(78.4630409672)),.2)
  eq(14**2,r*r+4*5*r*.2+4*25)
 if name=='opposite_rays':
  A,B,F=m['A'],m['B'],m['F']
  ra=hypot(A[0]-5,A[1]);rb=hypot(B[0]-5,B[1])
  eq(ra,8);eq(rb,4);eq((A[0]-5)/ra,.2);eq((B[0]-5)/rb,-.2)
  eq(hypot(A[0]-B[0],A[1]-B[1]),ra+rb)

# Existing comparison figures, analytical boundary, and range-plot endpoints.
for k,ts in [(Q(1,4),[(-1280+192*sqrt(17))/247,(-1280-192*sqrt(17))/247]),
             (4,[(5+3*sqrt(17))/8,(5-3*sqrt(17))/8])]:
 for t in ts:point((5+t,float(k)*t))
point((Q(17,5),-Q(32,15)))
for deg in [0,10,30,45,60,75,90]:
 L=96/abs(9-25*cos(radians(deg))**2)
 assert L>0
 if deg==0:eq(L,6)
 if deg==90:eq(L,Q(32,3))
eq(length(3,4,2),24);eq(length(3,4,.5),Q(96,11))
eq(length(3,4,2/sqrt(21)),8)
eq(length(3,4,sqrt(8/17)),12);eq(length(3,4,2*sqrt(6)),12)
proof=(UID/'03_proof.tex').read_text(encoding='utf8')
sections=re.split(r'\\textbf\{方法[一二三四]：',proof)[1:]
assert len(sections)==4
for sec,name in zip(sections,['root_projection','two_minima','vertical_parameter','focal_triangle']):
 assert f'assets/tikz/C087_{name}' in sec
for path in (ROOT/'assets/tikz').glob('C087_*.tex'):
 t=path.read_text(encoding='utf8');assert '\\scriptsize' not in t
 if 'x=0.39cm' in t:assert 'y=0.39cm' in t
meta=json.loads((UID/'meta.json').read_text(encoding='utf8'))
assert meta['id']=='C087' and meta['interactive']['has_diagram']
print(json.dumps(dict(status='PASS',parameter_cases=cases,equalities=checks,
 proof_methods_with_diagrams=4,figures=8,examples=4),indent=2))
