from pathlib import Path
import math,re,json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
for a,b in [(3,4),(4,3),(2,math.sqrt(5)),(1,.001)]:
 c=math.hypot(a,b);e=c/a;d=a*a/c
 for k in range(-200,201):
  y=k*b/40
  for sign in [-1,1]:
   x=sign*a*math.sqrt(1+(y/b)**2)
   close(math.hypot(x-c,y),e*abs(x-d))
   close(math.hypot(x+c,y),e*abs(x+d))
   assert abs(x-d)>0
for x in range(-7,8):
 for y in range(-5,6):close((x-5)**2+y*y-(25/9)*(x-9/5)**2,-16*(x*x/9-y*y/16-1))
for q,e in [(3,5/3),(.2,1.001),(4,3)]:
 k=e*e-1;h=-q/k;a=q*e/k;b=q*e/math.sqrt(k)
 for j in range(-50,51):
  y=j*b/10
  for sign in [-1,1]:
   x=h+sign*a*math.sqrt(1+(y/b)**2);close(math.hypot(x-q,y),e*abs(x))
s=(ROOT/'assets/tikz/C040_example_two_abscissas.tex').read_text(encoding='utf-8')
pts=re.findall(r'inner sep=1.8pt\] at \(([-\d.]+),([-\d.]+)\)',s)
checked=0
for xs,ys in pts:
 x,y=float(xs),float(ys)
 if abs(y)>1:
  close(x*x/4-y*y/5,1);close(math.hypot(x-3,y),6);checked+=1
assert checked==4,pts
for x,y in [(3.75,3),(-3.75,-3)]:close(math.hypot(x-5,y)/abs(x-1.8),5/3)
close((13/4)/(111/20),65/111)
x,y=56/5,math.sqrt(1539)/5
close(x*x/16-y*y/9,1);close(math.hypot(x-5,y),10);close(abs(x-16/5),8)
close(math.hypot(5-4,math.sqrt(63)),8)
for x in [-2,-1,0,1,2]:close(math.hypot(x,4*x/3),5*abs(x)/3)
m=json.loads((ROOT/'03_conic/C040_hyperbola_focus_directrix_ratio/meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C040 ' in (ROOT/'03_conic/C040_hyperbola_focus_directrix_ratio/main.tex').read_text(encoding='utf-8')
print('C040 PASS: 3208 two-branch states, 165 identity points, 606 general-model states, four actual figure intersections, examples and degeneration')
