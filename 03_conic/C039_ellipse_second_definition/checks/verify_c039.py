from pathlib import Path
import math,json,re
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
# Read the coordinates of the new same-scale three-panel diagram.
three=(ROOT/'assets/tikz/C039_three_point_ratio.tex').read_text(encoding='utf-8')
data=re.search(r'\{(2\.1/5/0,6\.9/0/3,11\.7/-5/0)\}',three)[1]
for row,pf,ph in zip(data.split(','),[1,5,9],[5/4,25/4,45/4]):
 _,x,y=map(float,row.split('/'))
 close(x*x/25+y*y/9,1)
 close(math.hypot(x-4,y),pf);close(abs(x-25/4),ph);close(pf/ph,4/5)
split=(ROOT/'assets/tikz/C039_directrix_distance_sum.tex').read_text(encoding='utf-8')
assert '(-6.25,2.4)--(3,2.4)' in split and '(3,2.4)--(6.25,2.4)' in split
x,y=3,12/5
left,right=abs(x+25/4),abs(x-25/4)
fl,fr=math.hypot(x+4,y),math.hypot(x-4,y)
close(left,37/4);close(right,13/4);close(left+right,25/2)
close(fl,37/5);close(fr,13/5);close(fl+fr,(4/5)*(left+right));close(fl+fr,10)
print('C039 PASS: 2884 ellipse states, 187 identity points, 1444 general ratio states; actual three-point ratios and split directrix distances; examples and minimum')
