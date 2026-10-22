from pathlib import Path
import math,re,json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
n=0
for a,b in [(.1,.03),(3,1),(3,3),(3,4),(3,5),(4,3),(3,math.sqrt(7))]:
 c=math.hypot(a,b);assert c>a and c>b
 for sign in [-1,1]:
  for k in range(-100,101):
   y=k*b/10;x=sign*a*math.sqrt(1+(y/b)**2)
   r1=math.hypot(x+c,y);r2=math.hypot(x-c,y)
   close(abs(r1-r2),2*a);close(r1*r1-r2*r2,4*c*x)
   close(r1,abs(c*x/a+a));close(r2,abs(c*x/a-a))
   close(x*x/a**2-y*y/b**2,1);n+=1
# Actual curve point in the distance-difference diagram.
s=(ROOT/'assets/tikz/C043_distance_difference.tex').read_text(encoding='utf-8')
y=float(re.search(r'\\fill \(5,([1-9][0-9.]+)\)',s)[1]);close(25/9-y*y/16,1)
r1=math.hypot(10,y);r2=y;close(r1,34/3);close(r2,16/3);close(r1-r2,6)
# Actual foci in all three fixed-a panels.
s=(ROOT/'assets/tikz/C043_opening_ratio.tex').read_text(encoding='utf-8')
cs=[float(x) for x in re.findall(r'\\fill \(([0-9.]+),0\)',s)];assert len(cs)==3
for b,c in zip([1,3,5],cs):close(c*c,9+b*b)
assert all(2*math.atan(b/3)<2*math.atan(bb/3) for b,bb in [(1,3),(3,5)])
close(math.hypot(3,4),5);close(9/9-16/16,0) # Q is NOT a curve point.
close(math.sqrt(16+9),5);close(9*16,144);close(9+16,25)
close(25-9,16);close(16-9,7);close(abs(7-1),6)
for c in [2,3]:assert c*c-9<=0
r=ROOT/'03_conic/C043_hyperbola_abc_relation';m=json.loads((r/'meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C043 ' in (r/'main.tex').read_text(encoding='utf-8')
print(f'C043 PASS: {n} two-branch distance, sign and equation states; actual diagram coordinates, opening angles, examples, boundary and metadata')
