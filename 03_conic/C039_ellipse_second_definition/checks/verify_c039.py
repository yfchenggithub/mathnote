from pathlib import Path
import math,json
ROOT=Path(__file__).resolve().parents[3]
def close(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8),(a,b)
for a,b in [(5,3),(4,math.sqrt(12)),(1,.001),(1,.9999)]:
 c=math.sqrt(a*a-b*b);e=c/a;d=a*a/c
 for k in range(721):
  t=math.radians(k/2);x,y=a*math.cos(t),b*math.sin(t)
  close(math.hypot(x-c,y)/(d-x),e)
  close(math.hypot(x+c,y)/(d+x),e)
  close(math.hypot(x-c,y),a-e*x)
# General arbitrary off-curve points check bidirectional identity independently.
a,b,c=5,3,4;e=c/a;d=a*a/c
for x in range(-8,9):
 for y in range(-5,6):close((x-c)**2+y*y-e*e*(x-d)**2,b*b*(x*x/(a*a)+y*y/(b*b)-1))
for q,e in [(2,.5),(1,.8),(3,.01),(2,.99)]:
 h=q/(1-e*e);a=q*e/(1-e*e);b=q*e/math.sqrt(1-e*e)
 for k in range(361):
  t=math.radians(k);x,y=h+a*math.cos(t),b*math.sin(t)
  close(math.hypot(x-q,y),e*abs(x))
# Exact points and distances in the mathematical illustrations.
x,y=3,12/5
close(x*x/25+y*y/9,1);close(math.hypot(x-4,y),13/5)
close(25/4-x,13/4);close(x+25/4,37/4)
close((13/5)/(37/4),52/185)
close(math.hypot(12/5,3-4),13/5)
close(math.hypot(2,2*math.sqrt(3)),4)
for k in range(721):
 t=math.radians(k/2);x,y=5*math.cos(t),3*math.sin(t)
 value=math.hypot(x-4,y)+.8*(6.25-x)
 assert value>=2-1e-9
close(math.hypot(5-4,0)+.8*(6.25-5),2)
m=json.loads((ROOT/'03_conic/C039_ellipse_second_definition/meta.json').read_text(encoding='utf-8'))
for uid in m['relations']['related_ids']:assert list((ROOT/'03_conic').glob(uid+'_*'))
assert r'\subsection{C039 ' in (ROOT/'03_conic/C039_ellipse_second_definition/main.tex').read_text(encoding='utf-8')
print('C039 PASS: 2884 ellipse states, 187 identity points, 1444 general ratio states, exact diagram lengths, examples and minimum')
