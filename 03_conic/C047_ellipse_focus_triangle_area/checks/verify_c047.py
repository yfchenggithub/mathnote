from pathlib import Path
import math,json,re
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8),(a,b)
n=0
for a,b in [(5,3),(5,4),(4,3),(4,math.sqrt(12)),(math.sqrt(10),math.sqrt(5)),(1,.999)]:
 c=math.sqrt(a*a-b*b);maximum=2*math.atan(c/b)
 for k in range(1,360):
  if k==180:continue
  t=math.radians(k);x=a*math.cos(t);y=b*math.sin(t)
  m=math.hypot(x+c,y);v=math.hypot(x-c,y)
  theta=math.atan2(2*c*abs(y),x*x+y*y-c*c)
  area=c*abs(y)
  close(m+v,2*a);close(area,b*b*math.tan(theta/2))
  assert area<=c*b+1e-8 and theta<=maximum+1e-8
  s=a+c;radius=area/s
  close(radius,(a-c)*math.tan(theta/2));n+=1
 close(c*b,b*b*math.tan(maximum/2))
# Actual tangent point / incircle in the TikZ model.
s=(ROOT/'assets/tikz/C047_incircle_proof.tex').read_text(encoding='utf-8')
assert r'(.8,2.4)' in s
I=(0,4/3);D=(.8,2.4);P=(0,3)
close(math.dist(I,D),4/3);close(math.dist(P,D),1)
close((D[0]-P[0])*(D[0]-I[0])+(D[1]-P[1])*(D[1]-I[1]),0)
close(abs(3*I[0]+4*I[1]-12)/5,4/3)
close(abs(-3*I[0]+4*I[1]-12)/5,4/3)
# Three actual curve points in the area/range illustration.
s=(ROOT/'assets/tikz/C047_area_angle_range.tex').read_text(encoding='utf-8')
pts=[(float(x),float(y)) for x,y in re.findall(r'inner sep=1.4pt\] at \(([-\d.]+),([-\d.]+)\)',s)]
assert len(pts)==3
for (x,y),expected in zip(pts,[0,6,12]):close(x*x/25+y*y/9,1);close(4*abs(y),expected)
# Example 1 independently verifies the angle from a dot product.
x=5*math.sqrt(33)/9;y=16*math.sqrt(3)/9
close(x*x/25+y*y/16,1)
m=math.hypot(x+3,y);v=math.hypot(x-3,y)
close((x*x+y*y-9)/(m*v),.5);close(3*y,16*math.sqrt(3)/3)
close(math.sqrt(5)*math.sqrt(5),5)
close(math.hypot(2,2*math.sqrt(3)),4);close(4*math.sqrt(3),12/math.sqrt(3))
assert 3*math.sqrt(7)<12
s=(ROOT/'assets/tikz/C047_equilateral_example.tex').read_text(encoding='utf-8')
y=float(re.search(r'\\fill \(0,([0-9.]+)\)',s)[1]);close(y*y,12);close(math.hypot(2,y),4)
r=ROOT/'03_conic/C047_ellipse_focus_triangle_area';m=json.loads((r/'meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C047 ' in (r/'main.tex').read_text(encoding='utf-8')
print(f'C047 PASS: {n} independent angle/area/inradius states; actual incircle, tangency and diagram coordinates; three examples, endpoints, infeasible angle and metadata')
