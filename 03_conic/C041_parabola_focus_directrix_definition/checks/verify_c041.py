from pathlib import Path
import math,re,json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
for p in [.01,2,4,6,10]:
 for k in range(-100,101):
  y=k*p/20;x=y*y/(2*p)
  radius=math.hypot(x-p/2,y)
  close(radius,x+p/2);assert radius>=p/2-1e-9
  # Circle centered at P goes through F and is tangent to x=-p/2.
  close(radius,abs(x+p/2))
for k in range(-100,101):
 y=k/10
 # Same focus (3,0), two directrices; independently check translated model.
 x1=y*y/12;x2=4-y*y/4
 close(math.hypot(x1-3,y),abs(x1+3));close(math.hypot(x2-3,y),abs(x2-5))
for L,expected in [(1,0),(2,1),(6,2)]:
 x=L-2
 ys=[] if x<0 else [0] if x==0 else [-math.sqrt(8*x),math.sqrt(8*x)]
 assert len(ys)==expected
 for y in ys:close(math.hypot(x-2,y),L);close(y*y,8*x)
# Check the actual two orange intersections in the source, not rounded display text.
s=(ROOT/'assets/tikz/C041_focal_radius_range.tex').read_text(encoding='utf-8')
pts=re.findall(r'inner sep=2pt\] at \(([-\d.]+),([-\d.]+)\)',s)
assert len(pts)==3,pts
for xs,ys in pts:
 x,y=float(xs),float(ys);close(y*y,8*x)
 if x:close(math.hypot(x-2,y),6)
 else:close(math.hypot(x-2,y),2)
close(math.hypot(3-3,6),6);close(3+3,6);close(6*6,12*3)
for x in [-3,0,2]:close(math.hypot(x,0),abs(x))
m=json.loads((ROOT/'03_conic/C041_parabola_focus_directrix_definition/meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C041 ' in (ROOT/'03_conic/C041_parabola_focus_directrix_definition/main.tex').read_text(encoding='utf-8')
print('C041 PASS: 1005 distance/tangent-circle states; 201 same-focus comparisons; actual range intersections, equality and metadata')
