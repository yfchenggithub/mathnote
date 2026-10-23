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

# Perpendicular-bisector construction: independent midpoint/dot product checks.
for p in [.1,2,4,10]:
 for j in range(-60,61):
  t=j*p/15;x=t*t/(2*p)
  F=(p/2,0);H=(-p/2,t);M=(0,t/2);P=(x,t)
  close((P[0]-M[0])*(F[0]-H[0])+(P[1]-M[1])*(F[1]-H[1]),0)
  close(math.dist(P,F),math.dist(P,H))
  radius=math.dist(P,F);fh=math.dist(F,H)
  assert p<=fh+1e-8 and fh<=2*radius+1e-8
  close(radius-p/2,x)
  assert (abs(radius-p/2)<1e-8)==(j==0)
# Both literal coordinate models in the Pythagoras picture.
for x,y in [(.5,2),(4,4*math.sqrt(2))]:
 close(y*y,8*x)
 ph=x+2;pq=abs(x-2)
 close(ph*ph-pq*pq,y*y)
 close(math.hypot(x-2,y),ph)
close(2.5-1.5,1);close(2.5+1.5,4)
# Concrete construction and strict/equality diagrams.
close(4,math.dist((2,4),(2,0)))
close(math.dist((-2,4),(2,0)),4*math.sqrt(2))
close(math.dist((0,0),(2,0)),2)
# Oblique parabola plotted with t=x-y: point-line distance, not just equation.
for j in range(-120,121):
 t=j/40;x=(1+t*t/4+t)/2;y=(1+t*t/4-t)/2
 close((x-y)**2,4*(x+y-1))
 close(math.hypot(x-1,y-1),abs(x+y)/math.sqrt(2))
 hx=(x-y)/2;hy=(y-x)/2
 close(hx+hy,0);close((x-hx)*(1)+(y-hy)*(-1),0)
close(math.dist((2,0),(1,1)),math.dist((2,0),(1,-1)))
# Added applications and their actual answers.
for x,y in [(5,2*math.sqrt(10)),(5,-2*math.sqrt(10))]:
 close(y*y,8*x);close(math.hypot(x-2,y),7)
for x,y in [(2,2*math.sqrt(2)),(2,-2*math.sqrt(2))]:
 close(y*y,4*x);close(math.hypot(x-1,y),3);close(abs(x+1),3)
print('C041 supplementary PASS: 484 construction/minimum states, both Pythagoras positions, 241 oblique states and added applications')

# Arbitrary-line proof: include reversed normals and a horizontal directrix.
for a,b,c,u,v in [(1,1,0,1,1),(2,-3,1,-2,3),(0,2,-8,3,-2)]:
 den=a*a+b*b;g=a*u+b*v+c
 p=abs(g)/math.sqrt(den);sg=1 if g>0 else -1
 nx=sg*a/math.sqrt(den);ny=sg*b/math.sqrt(den)
 dx=u-g*a/den;dy=v-g*b/den;vx=(u+dx)/2;vy=(v+dy)/2
 close(a*dx+b*dy+c,0);close(math.hypot(u-dx,v-dy),p)
 for j in range(-60,61):
  r=j*p/20;axis=r*r/(2*p)
  x=vx+axis*nx-r*ny;y=vy+axis*ny+r*nx
  close(math.hypot(x-u,y-v),abs(a*x+b*y+c)/math.sqrt(den))
print('C041 general-line PASS: 363 rotated/translated states including both normal signs')
