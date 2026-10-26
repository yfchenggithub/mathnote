from pathlib import Path
import math,json
def eq(a,b):assert math.isclose(a,b,rel_tol=3e-10,abs_tol=3e-10),(a,b)
states=0
for a,e in [(2,.5),(5,.8),(3,.2),(4,.95)]:
 c=a*e;b=a*math.sqrt(1-e*e)
 for left in [False,True]:
  f=-c if left else c
  for deg in range(180):
   q,v=math.cos(math.radians(deg)),math.sin(math.radians(deg))
   # Independent substitution F+t*u into the Cartesian ellipse equation.
   qa=q*q/(a*a)+v*v/(b*b);qb=2*f*q/(a*a);qc=f*f/(a*a)-1
   root=math.sqrt(qb*qb-4*qa*qc)
   signed=-.5*(qb+math.copysign(root,qb))
   ts=sorted([signed/qa,qc/signed],reverse=True)
   assert ts[0]>0>ts[1]
   r,s=ts[0],-ts[1]
   eq(r,b*b/(a+f*q));eq(s,b*b/(a-f*q))
   eq(r/s,(a-f*q)/(a+f*q));eq(r+s,2*a*b*b/(a*a-c*c*q*q))
   assert 2*b*b/a-1e-9<=r+s<=2*a+1e-9
   for t in ts:
    x,y=f+t*q,t*v
    eq(x*x/a**2+y*y/b**2,1)
    eq(math.hypot(x-c,y)+math.hypot(x+c,y),2*a)
    distance=(a*a/c-x) if not left else (x+a*a/c)
    assert distance>0
    eq(abs(t),e*distance)
   if not left:
    R=r/s;eq((1-R)/(e*(1+R)),q)
    assert (1-e)/(1+e)-1e-12<=R<(1+e)/(1-e)+1e-12
    # Cosine theorem for both focal triangles, including algebraic degenerate case.
    eq((2*a-r)**2,4*c*c+r*r+4*c*r*q)
    eq((2*a-s)**2,4*c*c+s*s-4*c*s*q)
   states+=1
# Coordinates and distances used by the figures and five examples.
F=(4,0);A=(65/14,9*math.sqrt(3)/14);B=(2.5,-3*math.sqrt(3)/2)
for x,y in [A,B]:eq(x*x/25+y*y/9,1)
eq(math.dist(A,F),9/7);eq(math.dist(B,F),3);eq((9/7)/3,3/7);eq(9/7+3,30/7)
eq(A[0]-4,(9/7)*.5);eq(B[0]-4,-3*.5)
eq(6.25-A[0],9/4-(9/7)*.5);eq(6.25-B[0],9/4+3*.5)
eq((5-2*math.sqrt(2))/(5+2*math.sqrt(2)),(33-20*math.sqrt(2))/17)
q=-2/3;eq((1-.5*q)/(1+.5*q),2)
for pt in [(-.5,3*math.sqrt(5)/4),(7/4,-3*math.sqrt(5)/8)]:
 eq(pt[0]**2/4+pt[1]**2/3,1)
eq(math.dist((1,0),(-.5,3*math.sqrt(5)/4)),9/4)
eq(math.dist((1,0),(7/4,-3*math.sqrt(5)/8)),9/8)
eq(2*9/5,18/5)
# Pure projection and triangle angles use the same representative chord.
eq(math.hypot(9/14,9*math.sqrt(3)/14),9/7)
eq(math.hypot(1.5,3*math.sqrt(3)/2),3)
for pt,target in [(A,-.5),(B,.5)]:
 w=(pt[0]-4,pt[1]);eq((-w[0])/math.hypot(*w),target)
base=Path('03_conic/C056_ellipse_focal_chord_ratio')
json.loads((base/'meta.json').read_text(encoding='utf8'))
figures=['statement_overview','pure_projection','directrix_projection','two_focal_triangles','angle_comparison','chord_extremes','left_right_focus']
for stem in figures:
 s=Path(f'assets/tikz/C056_{stem}.tex').read_text(encoding='utf8');assert '\\tiny' not in s and '\\scriptsize' not in s
for name in ['main.tex','source.tex']:
 assert (base/name).read_bytes()==(Path('.tmp/C056_tikz_review/before')/name).read_bytes()
proof=(base/'03_proof.tex').read_text(encoding='utf8')
for marker in ['方法一','方法二','方法三','直觉补充']:assert marker in proof
ex=(base/'04_examples.tex').read_text(encoding='utf8')
for i in range(1,6):assert f'例 {i}' in ex
result={'status':'PASS','intersection_states':states,'ellipse_parameter_pairs_a_e':[[2,.5],[5,.8],[3,.2],[4,.95]],'focus_choices':2,'angles_degrees':'0..179','figures':7,'examples':5,'main_source_preserved':True}
Path('.tmp/C056_tikz_review/math_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
