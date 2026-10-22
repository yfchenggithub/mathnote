from pathlib import Path
import math,re,json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
n=0
for a in [.1,1,5,17]:
 for ratio in [.01,.3,.6,2**-.5,.9,.999]:
  b=a*ratio;c=math.sqrt(a*a-b*b)
  close(math.hypot(b,c),a);assert a>b>0 and a>c>0
  for k in range(361):
   t=math.radians(k);x=a*math.cos(t);y=b*math.sin(t)
   close(math.hypot(x-c,y)+math.hypot(x+c,y),2*a)
   close(math.hypot(x-c,y),a-c*x/a)
   close(math.hypot(x+c,y),a+c*x/a)
   n+=1
# Independently check actual focal coordinates in the three comparison panels.
s=(ROOT/'assets/tikz/C042_b_c_order.tex').read_text(encoding='utf-8')
bs=[float(x) for x in re.findall(r'ellipse \(5 and ([0-9.]+)\)',s)]
cs=[float(x) for x in re.findall(r'inner sep=1.5pt\] at \(([0-9.]+),0\)',s)]
assert len(bs)==len(cs)==3
for b,c in zip(bs,cs):close(b*b+c*c,25)
assert bs[0]>cs[0] and abs(bs[1]-cs[1])<1e-9 and bs[2]<cs[2]
close(math.sqrt(25-9),4);close(16+9,25)
for x in [-4,4]:close(x*x+3*3,25)
close(10*10,6*6+8*8)
a=4;b=2*math.sqrt(3);c=2;close(a*a,b*b+c*c);close(c/a,.5)
close(math.hypot(3,4),5);assert math.sqrt(34)>5>4
s=(ROOT/'assets/tikz/C042_ellipse_hyperbola.tex').read_text(encoding='utf-8')
fs=[float(x) for x in re.findall(r'\\fill \(([0-9.]+),0\)',s)]
assert len(fs)==2;close(fs[0]**2,16);close(fs[1]**2,34)
r=ROOT/'03_conic/C042_ellipse_abc_relation'
m=json.loads((r/'meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C042 ' in (r/'main.tex').read_text(encoding='utf-8')
print(f'C042 PASS: {n} independent distance-sum / positive-root states; actual three b/c panels, focal coordinates, circle construction, examples and metadata')
