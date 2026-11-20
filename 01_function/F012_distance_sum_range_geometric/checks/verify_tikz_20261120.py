from fractions import Fraction as Q
from math import hypot,sqrt,isclose
from pathlib import Path
import json
count=0
for m in [-2,0,1,3]:
 for n in [-2,0,1,3]:
  for a in [Q(1,2),Q(1),Q(2)]:
   for b in [Q(1),Q(3)]:
    x=(b*m+a*n)/(a+b);d2=(m-n)**2+(a+b)**2
    assert b*(x-m)==a*(n-x)
    assert (x-m)**2+a*a==(a/(a+b))**2*d2
    assert (x-n)**2+b*b==(b/(a+b))**2*d2
    for t in [Q(-4),Q(-1),Q(0),Q(1),Q(4)]:
     u=t-m;v=n-t
     assert (u*u+a*a)*(v*v+b*b)-(u*v+a*b)**2==(b*u-a*v)**2
     val=hypot(float(u),float(a))+hypot(float(v),float(b))
     assert val>=sqrt(float(d2))-1e-12
     count+=1
f=lambda x:hypot(x-1,2)+hypot(x-3,3)
assert isclose(f(9/5),sqrt(29))
assert isclose(f(0),sqrt(5)+3*sqrt(2)) and isclose(f(1),2+sqrt(13)) and isclose(f(2),sqrt(5)+sqrt(10))
assert 3**2+4**2==5**2 and Q(11,4)==(3*Q(2)+Q(5))/4
assert (2**2+2**2)*(0**2+3**2)-(2*0+2*3)**2==(3*2-2*0)**2
out=Path('build/F012-F015-visual-review-20261120/F012/math-checks.json')
out.write_text(json.dumps({'status':'PASS','exact_and_numeric_general_parameter_cases':count,'manual_audit':'3 proofs, examples 0-5 and practice; a,b>0, m<n/m=n/m>n, constrained endpoints, squared identity and coordinate scales.'},indent=2),encoding='utf-8');print('PASS',count)
