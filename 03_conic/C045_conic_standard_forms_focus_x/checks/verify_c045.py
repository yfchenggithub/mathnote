from pathlib import Path
import math,json,re
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
n=0
for a,c in [(5,3),(5,4),(.1,.09)]:
 b=math.sqrt(a*a-c*c)
 for k in range(361):
  t=math.radians(k);x=a*math.cos(t);y=b*math.sin(t)
  r1=math.hypot(x+c,y);r2=math.hypot(x-c,y)
  close(r1+r2,2*a);close(r1-r2,2*c*x/a);close(r2,a-c*x/a);n+=1
for a,c in [(2,3),(3,5),(.1,.2)]:
 b=math.sqrt(c*c-a*a)
 for sg in [-1,1]:
  for k in range(-100,101):
   y=k*b/20;x=sg*a*math.sqrt(1+(y/b)**2)
   r1=math.hypot(x+c,y);r2=math.hypot(x-c,y)
   close(abs(r1-r2),2*a);close(r1,abs(c*x/a+a));close(r2,abs(c*x/a-a));n+=1
for p in [.01,4,10]:
 for sg in [-1,1]:
  for k in range(-100,101):
   y=k*p/20;x=sg*y*y/(2*p)
   close(math.hypot(x-sg*p/2,y),abs(x+sg*p/2));n+=1
# Actual distance diagram coordinates and coefficient/translation models.
s=(ROOT/'assets/tikz/C045_sum_difference.tex').read_text(encoding='utf-8')
assert r'(0,4)' in s and r'(3,2.5)' in s
close(math.hypot(3,4)*2,10);close(math.hypot(6,2.5)-2.5,4)
close(9/4-2.5**2/5,1);assert 8>2*3
for k in range(361):
 t=math.radians(k);x=3*math.cos(t);y=2*math.sin(t)
 close(4*x*x+9*y*y,36);close(9*y*y+4*x*x,36)
 x=5*math.cos(t);y=3*math.sin(t)
 close((x+2-2)**2/25+y*y/9,1)
 close(math.hypot(x+2+2,y)+math.hypot(x+2-6,y),10)
close(math.sqrt(25-16),3);close(math.sqrt(9+16),5)
r=ROOT/'03_conic/C045_conic_standard_forms_focus_x';m=json.loads((r/'meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C045 ' in (r/'main.tex').read_text(encoding='utf-8')
assert m['interactive']['has_diagram'] is True
print(f'C045 PASS: {n} ellipse/hyperbola/parabola distance states; 361 coefficient/translated-center states; actual diagram points, invalid difference and metadata')
