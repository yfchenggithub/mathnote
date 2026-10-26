import math,json
from pathlib import Path
def eq(a,b):assert math.isclose(a,b,rel_tol=2e-9,abs_tol=2e-9),(a,b)
maps=[lambda x,y:(x,y),lambda x,y:(-x,y),lambda x,y:(y,x),lambda x,y:(y,-x)]
states=0
for p in [.5,2,6]:
 for deg in range(1,180):
  dx,dy=math.cos(math.radians(deg)),math.sin(math.radians(deg))
  a,b,c=dy*dy,-2*p*dx,-p*p
  delta=math.sqrt(b*b-4*a*c);q=-.5*(b+math.copysign(delta,b))
  ts=sorted([q/a,c/q],reverse=True)
  pts=[(p/2+t*dx,t*dy) for t in ts]
  (x1,y1),(x2,y2)=pts
  assert ts[0]>0>ts[1] and y1*y2<0
  eq(x1*x2,p*p/4);eq(y1*y2,-p*p)
  ka,kb=p/y1,p/y2;eq(ka*kb,-1)
  X,Y=-p/2,(y1+y2)/2
  eq(y1*Y,p*(X+x1));eq(y2*Y,p*(X+x2))
  if deg<90:
   h,k=x1-p/2,p/2-x2;u,v=y1,-y2
   assert h>0 and k>0
   eq(h/u,k/v);eq(u*v,p*p)
  for i,transform in enumerate(maps):
   (ax,ay),(bx,by)=[transform(*pt) for pt in pts]
   eq(ax*bx,p*p/4 if i<2 else -p*p)
   eq(ay*by,-p*p if i<2 else p*p/4)
   f=transform(p/2,0)
   eq(math.dist((ax,ay),f),abs(ts[0]));eq(math.dist((bx,by),f),abs(ts[1]))
   states+=1
# Exact geometry used by each main diagram and examples.
for ya,yb in [(2,-2),(4,-1),(1,-4)]:
 xa,xb=ya*ya/4,yb*yb/4
 eq(xa*xb,1);eq(ya*yb,-4)
 eq((xa-1)*yb,(xb-1)*ya)
eq(3/4,(3/4)/1) # Pure triangles: h/u=k/v.
eq(4*1,4);eq((-2)*2,-4)
# Example 2: independent intersection along the ray from focus.
p=4;xa=3;ya=math.sqrt(24);yb=-16/ya;xb=yb*yb/8
eq(xb,4/3);eq(math.hypot(xb-2,yb),10/3);eq(1/5+1/(10/3),.5)
for m in [-2,-.5,0,.75,3]:
 ys=[2*m+math.sqrt(4*m*m+4),2*m-math.sqrt(4*m*m+4)]
 eq(sum(ys),4*m);eq(math.prod(ys),-4)
 for y in ys:eq(y*(2*m),2*(-1+y*y/4))
eq(4*1.5,2*(-1+4));eq(-1*1.5,2*(-1+.25))
eq((2*math.sqrt(2))*(-2*math.sqrt(2)),-8)
# Upward-opening variant p=3, one representative focal chord.
pa=(6,6);pb=(-1.5,.375)
for x,y in [pa,pb]:eq(x*x,6*y)
eq(pa[0]*pb[0],-9);eq(pa[1]*pb[1],9/4)

base=Path('03_conic/C055_parabola_focal_chord_product')
json.loads((base/'meta.json').read_text(encoding='utf8'))
for stem in ['pure_similarity','coordinate_mapping','product_comparison','tangent_right_angle','validity_comparison','four_openings','statement_overview']:
 s=Path(f'assets/tikz/C055_{stem}.tex').read_text(encoding='utf8')
 assert '\\tiny' not in s and '\\scriptsize' not in s
ex=(base/'04_examples.tex').read_text(encoding='utf8')
for marker in ['例 1','例 2','例 3','例 4','高价值变式']:assert marker in ex
# Main/source and original small figure must not have been changed by this task.
for name in ['main.tex','source.tex']:
 assert (base/name).read_bytes()==(Path('.tmp/C055_tikz_review/before')/name).read_bytes()
result={'status':'PASS','intersection_states':states,'p_values':[.5,2,6],'inclinations_degrees':'1..179','openings':4,'figures':7,'examples':4,'variant':1,'main_source_preserved':True}
Path('.tmp/C055_tikz_review/math_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
