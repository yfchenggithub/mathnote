from pathlib import Path
import math,json,re
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
n=0
for typ,a,b in [('ellipse',5,4),('ellipse',10,6),('ellipse',3,.1),('hyperbola',3,4),('hyperbola',4,3),('hyperbola',.3,2)]:
 c=math.sqrt(a*a+(-1 if typ=='ellipse' else 1)*b*b);d=a*a/c;e=c/a
 close(abs(a-c)/abs(a-d),e)
 for k in range(-180,181):
  if typ=='ellipse':x=a*math.cos(math.radians(k));y=b*math.sin(math.radians(k))
  else:y=k*b/30;x=(1 if k%2 else -1)*a*math.sqrt(1+(y/b)**2)
  radius=math.hypot(x-c,y);dist=abs(x-d);assert dist>0
  close(radius/dist,e);close(radius,abs(a-c*x/a));n+=1
# All three plotted models share the ACTUAL same F=(2,0), l:x=0.
for typ,e in [('ellipse',.6),('parabola',1),('hyperbola',1.5)]:
 for k in range(-100,101):
  y=k/30
  if typ=='ellipse':
   t=k*math.pi/100;x=3.125+1.875*math.cos(t);y=1.5*math.sin(t)
  elif typ=='parabola':x=1+y*y/4
  else:x=-1.6+(1 if k%2 else -1)*2.4*math.sqrt(1+y*y/7.2)
  close(math.hypot(x-2,y)/abs(x),e)
for x,y,e in [(3.125,1.5,.6),(2,2,1),(2,3,1.5)]:close(math.hypot(x-2,y)/abs(x),e)
s=(ROOT/'assets/tikz/C044_paired_directrix_example.tex').read_text(encoding='utf-8')
y=float(re.search(r'\\fill \(7.5,([0-9.]+)\)',s)[1]);x=7.5
close(x*x/100+y*y/36,1);close(math.hypot(x-8,y),4)
close(abs(x-12.5),5);close(abs(x+12.5),20);close(4/5,.8);close(4/20,.2)
close(math.sqrt(25-16)/5,.6);close(math.sqrt(16+9)/4,1.25)
for scale in [.1,1,2,10]:close(3*scale/(5*scale),.6)
s=(ROOT/'assets/tikz/C044_ellipse_shape_boundary.tex').read_text(encoding='utf-8')
bs=[float(x) for x in re.findall(r'ellipse \(3 and ([0-9.]+)\)',s)]
assert len(bs)==3
for e,b in zip([0,.6,.95],bs):close(b*b/9+e*e,1)
assert bs[0]>bs[1]>bs[2]>0
r=ROOT/'03_conic/C044_eccentricity_geometric_algebraic';m=json.loads((r/'meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C044 ' in (r/'main.tex').read_text(encoding='utf-8')
print(f'C044 PASS: {n} independent focal ratios and vertex states; 603 shared-focus/directrix states; actual example/shape coordinates, scaling, boundary and metadata')
