from pathlib import Path
import math,json,re
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
n=0
for typ in ['ellipse','hyperbola']:
 for a in [.1,1,3,5,20]:
  for ratio in [.01,.3,.6,.9,.999]:
   b=a*ratio if typ=='ellipse' else a*ratio*3
   c=math.sqrt(a*a+(-1 if typ=='ellipse' else 1)*b*b);h=b*b/a
   for sg in [-1,1]:
    x=sg*c;d=sg*a*a/c
    for sign in [-1,1]:
     y=sign*h
     close(x*x/a**2+(1 if typ=='ellipse' else -1)*y*y/b**2,1)
     close(abs(y),(c/a)*abs(x-d));n+=1
   close(2*h,2*b*b/a)
for p in [.01,1,4,20]:
 for sg in [-1,1]:
  for sign in [-1,1]:
   x=sg*p/2;y=sign*p
   close(y*y,sg*2*p*x);close(math.hypot(x-sg*p/2,y),p)
   close(abs(x+sg*p/2),p);n+=1
# Parse actual slanted chord endpoints, independently verify incidence and length.
s=(ROOT/'assets/tikz/C046_latus_vs_oblique_chord.tex').read_text(encoding='utf-8')
pts=[(float(x),float(y)) for x,y in re.findall(r'inner sep=1.4pt\] at \(([-\d.]+),([-\d.]+)\)',s)]
assert len(pts)==4
for x,y in pts:close(x*x/25+y*y/9,1)
(x1,y1),(x2,y2)=pts[2:]
close(y1,x1-4);close(y2,x2-4);close(math.hypot(x2-x1,y2-y1),90/17)
close(math.hypot(pts[1][0]-pts[0][0],pts[1][1]-pts[0][1]),18/5)
# Main figure actually uses the listed coordinates, not rounded labels.
s=(ROOT/'assets/tikz/C046_three_latus_recta.tex').read_text(encoding='utf-8')
pts=[(float(x),float(y)) for x,y in re.findall(r'fill=orange!85!black,circle,inner sep=1.4pt\] at \(([-\d.]+),([-\d.]+)\)',s)]
assert len(pts)==6
for x,y in pts[:2]:close(x*x/25+y*y/9,1)
for x,y in pts[2:4]:close(x*x/9-y*y/16,1)
for x,y in pts[4:]:close(y*y,8*x)
close(2*9/4,9/2);close(7/16+(9/4)**2/9,1)
a=2/math.sqrt(3);close(2/a,math.sqrt(3));assert a>1
close((1/math.sqrt(3))**2/a**2+(math.sqrt(3)/2)**2,1)
close(2*2/2,2);close(2*1,2)
r=ROOT/'03_conic/C046_conic_latus_rectum_length';m=json.loads((r/'meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C046 ' in (r/'main.tex').read_text(encoding='utf-8')
print(f'C046 PASS: {n} endpoints and independent focus/directrix states; actual four oblique/comparison endpoints, six main-diagram endpoints, examples and metadata')
