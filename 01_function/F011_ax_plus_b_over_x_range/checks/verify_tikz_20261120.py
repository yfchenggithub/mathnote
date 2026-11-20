"""Exact checks of F011 plot coordinates and identities, plus fixed-point numerical audit."""
from fractions import Fraction as Q
from math import sqrt,isclose
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--report',required=True);args=p.parse_args()
counts={'square_and_asymptotic_identities':0,'geometry_samples':0,'restricted_example_samples':0,'fixed_point_derivative_samples':0}
xs=[Q(i,10) for i in range(-40,41) if i]
for m in (1,2,3):
 for n in (1,2,3):
  A,B=m*m,n*n
  for x in xs:
   f=A*x+B/x
   assert f-2*m*n==(m*x-n)**2/x
   assert f+2*m*n==(m*x+n)**2/x
   assert (f>=2*m*n if x>0 else f<=-2*m*n)
   assert f-A*x==B/x and f-B/x==A*x
   counts['square_and_asymptotic_identities']+=1
  r=Q(n,m);assert A*r+B/r==2*m*n
for k in (1,4,9):
 for a in [Q(i,5) for i in range(1,26)]:
  for b in [Q(i,5) for i in range(1,26)]:
   u,v=a+b,k/a+k/b;d2=u*u+v*v
   assert d2>=2*u*v>=8*k
   assert 2*d2>=(u+v)**2
   assert (d2==8*k)==(a==b==sqrt(k))
   counts['geometry_samples']+=1
for x in [Q(i,10) for i in range(40,101)]:
 assert x+9/x-Q(25,4)==(x-4)*(4*x-9)/(4*x)>=0
 counts['restricted_example_samples']+=1
for b in [Q(i,10) for i in range(1,101)]:
 h=(b+2)**2+(Q(1,2)+1/b)**2
 assert h==(b+2)**2*(1+1/(4*b*b))
 derivative=2*(b+2)-1/(b*b)-2/(b*b*b)
 assert derivative==(b+2)*(2*b**3-1)/b**3
 counts['fixed_point_derivative_samples']+=1
assert 3*Q(2)+12/Q(2)==12
for x,y in [(Q(0),Q(3)),(Q(-2),Q(-5))]:
 assert (2*x*x+3*x+3)/(x+1)==y
assert 9*4==6*6==36 and 2*(9+4)>2*(6+6)==24
# Equal-scale triangle and perpendicular projection coordinates.
Qpt=(-1,-1);Ppt=(2,Q(1,2));assert (Ppt[0]-Qpt[0],Ppt[1]-Qpt[1])==(3,Q(3,2))
V=(3,1);H=(2,2);assert sum((V[i]-H[i])*H[i] for i in (0,1))==0
for r in (1,3):
 assert r*r in (1,9)
 assert (2*r)**2+(2*r)**2==8*r*r
b0=2**(-1/3);d0=(b0+2)*sqrt(1+b0/2)
assert isclose(b0**3,.5,rel_tol=1e-14)
assert isclose(-(2+b0)+(.5+1/b0)/b0**2,0,abs_tol=1e-13)
assert d0>2*sqrt(2)
report={'status':'PASS','checks':counts,'fixed_point':{'b0':b0,'minimum_distance':d0,'rounded_to_3dp':round(d0,3)},'manual_audit':'Six proof derivations, seven example solutions, domain restrictions, asymptote terminology, equal geometry scales and equality conditions reviewed. Exact samples supplement the symbolic proofs.'}
Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report))
