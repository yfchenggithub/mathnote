from pathlib import Path
import math,re,json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
for a,b in [(3,4),(3,math.sqrt(7)),(2,math.sqrt(5)),(1,.001)]:
 c=math.hypot(a,b)
 for k in range(-200,201):
  y=k*b/40
  for sign in [-1,1]:
   x=sign*a*math.sqrt(1+(y/b)**2)
   r1,r2=math.hypot(x+c,y),math.hypot(x-c,y)
   close(abs(r1-r2),2*a);close(r1-r2,sign*2*a)
   close(r1,abs(c*x/a+a));close(r2,abs(c*x/a-a))
for x,y in [(3.75,3),(-3.75,-3)]:
 close(x*x/9-y*y/16,1)
 close(abs(math.hypot(x+5,y)-math.hypot(x-5,y)),6)
s=(ROOT/'assets/tikz/C037_example_feasibility.tex').read_text(encoding='utf-8')
x,y=map(float,re.search(r'inner sep=2pt\] at \(([-\d.]+),([-\d.]+)\)',s).groups())
close(math.hypot(x+5,y),7);close(math.hypot(x-5,y),13)
close(x*x/9-y*y/16,1)
for x,y in [(-6,4*math.sqrt(3)),(-6,-4*math.sqrt(3))]:
 close(math.hypot(x+5,y),7);close(math.hypot(x-5,y),13)
for x in [-10,-5,5,10]:close(abs(abs(x+5)-abs(x-5)),10)
for y in [-10,0,10]:close(math.hypot(5,y)-math.hypot(-5,y),0)
assert 7+1<10 and abs(13-7)<10<13+7
m=json.loads((ROOT/'03_conic/C037_hyperbola_first_definition/meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C037 ' in (ROOT/'03_conic/C037_hyperbola_first_definition/main.tex').read_text(encoding='utf-8')
print('C037 PASS: 3208 sampled states on both branches; actual figure point, both example points, boundaries, metadata')
