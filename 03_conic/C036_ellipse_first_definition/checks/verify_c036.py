from pathlib import Path
import math, re, json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b): assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
# Independent distance model, including both axes and near-degenerate ellipses.
for a,c in [(5,3),(5,4),(3,math.sqrt(5)),(1,.9999)]:
 b=math.sqrt(a*a-c*c)
 for k in range(721):
  t=math.radians(k/2);x,y=a*math.cos(t),b*math.sin(t)
  r1,r2=math.hypot(x+c,y),math.hypot(x-c,y)
  close(r1+r2,2*a);close(r1,a+c*x/a);close(r2,a-c*x/a)
  assert a+c*x/a>0 and a-c*x/a>0
# True coordinates in final example drawing; distance, angle and area checked independently.
s=(ROOT/'assets/tikz/C036_example_triangle.tex').read_text(encoding='utf-8')
x,y=map(float,re.search(r'very thick\] \(-3,0\)--\(([-\d.]+),([-\d.]+)\)',s).groups())
r1,r2=math.hypot(x+3,y),math.hypot(x-3,y)
close(x*x/25+y*y/16,1);close(r1+r2,10)
close(((x+3)*(x-3)+y*y)/(r1*r2),.5)
close(3*y,16*math.sqrt(3)/3)
# Example 2 and boundary equality, with endpoints included.
x,y=-1.25,math.sqrt(135)/4
close(x*x/25+y*y/9,1);close(math.hypot(x+4,y),4);close(math.hypot(x-4,y),6)
for x in [-3,-2,0,2,3]:close(abs(x+3)+abs(x-3),6)
for x in [-4,4]:assert abs(x+3)+abs(x-3)>6
# Sample actual points in constant-sum drawing.
s=(ROOT/'assets/tikz/C036_constant_sum.tex').read_text(encoding='utf-8')
pts=re.findall(r'--\(([-\d.]+),([-\d.]+)\)',s)
for xs,ys in pts:
 x,y=float(xs),float(ys);close(x*x/25+y*y/16,1);close(math.hypot(x+3,y)+math.hypot(x-3,y),10)
m=json.loads((ROOT/'03_conic/C036_ellipse_first_definition/meta.json').read_text(encoding='utf-8'))
assert m['id']=='C036' and m['interactive']['has_diagram']
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*')),uid
assert r'\subsection{C036 ' in (ROOT/'03_conic/C036_ellipse_first_definition/main.tex').read_text(encoding='utf-8')
print('C036 PASS: 2884 sampled ellipse states, source figure coordinates, angle, area, examples, boundaries and metadata')

