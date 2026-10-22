from pathlib import Path
import math,json,re
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9),(a,b)
for p in [.01,2,4,10]:
 for k in range(-100,101):
  t=k*p/20
  u=t*t/(2*p)
  for sign in [-1,1]:
   x,y=sign*u,t;fx=sign*p/2
   close(math.hypot(x-fx,y),abs(x+fx))
   # Swapped coordinates give vertical parabolas with identical lengths.
   close(math.hypot(t,sign*u-fx),abs(sign*u+fx))
# Geometry construction H=(-p/2,h), M=(0,h/2), P=(h²/(2p),h).
for p,h in [(2,2),(4,-3),(.5,0),(.5,5)]:
 x,y=h*h/(2*p),h
 close((x)*(p)+(y-h/2)*(-h),0) # PM perpendicular to FH (FH=(p,-h))
 close(math.hypot(x-p/2,y),x+p/2)
for x,y,p in [(2,4,4),(2,1,2)]:
 if p==4:close(math.hypot(x-p/2,y),x+p/2)
 else:close(math.hypot(x,y-p/2),y+p/2)
# Minimum proof, unrestricted sample along whole parabola.
for k in range(-400,401):
 y=k/20;x=y*y/4
 value=math.hypot(x-3,y-2)+math.hypot(x-1,y)
 assert value>=4-1e-10
close(math.hypot(1-3,2-2)+math.hypot(1-1,2),4)
for x in [-10,0,10]:close(math.hypot(x,0),abs(x))
for x,y in [(0,1),(2,-3)]:assert math.hypot(x,y)>abs(x)
# Actual equality and minimum points, curve equations and metadata.
s=(ROOT/'assets/tikz/C038_equal_distance.tex').read_text(encoding='utf-8')
assert '(1,2)' in s and '(-1,2)' in s and '(1,0)' in s
s=(ROOT/'assets/tikz/C038_minimum_broken_path.tex').read_text(encoding='utf-8')
assert '(1,2)' in s and '(3,2)' in s and '(4,4)' in s
for x,y in [(1,2),(4,4)]:close(y*y,4*x)
m=json.loads((ROOT/'03_conic/C038_parabola_definition_focus_directrix/meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C038 ' in (ROOT/'03_conic/C038_parabola_definition_focus_directrix/main.tex').read_text(encoding='utf-8')
print('C038 PASS: 3216 directional states, construction, 801 minimum samples, equality, degenerate case, metadata')
