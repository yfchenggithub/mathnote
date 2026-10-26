from pathlib import Path
import math,json
def eq(a,b):assert math.isclose(a,b,rel_tol=3e-9,abs_tol=3e-9),(a,b)
two=one=same=cross=0
models=[(3,4),(2,4),(1,1),(2,1)]
for a,b in models:
 c=math.hypot(a,b);e=c/a;p=b*b/a;K=2/p
 for sign in [1,-1]:
  f=sign*c
  for deg in range(180):
   dx,dy=math.cos(math.radians(deg)),math.sin(math.radians(deg))
   # Substitute F+t*(dx,dy) into the Cartesian equation, independently of focal formulas.
   qa=dx*dx/a**2-dy*dy/b**2;qb=2*f*dx/a**2;qc=f*f/a**2-1
   if abs(qa)<1e-13:
    t=-qc/qb;x,y=f+t*dx,t*dy
    eq(x*x/a**2-y*y/b**2,1);one+=1;continue
   delta=math.sqrt(qb*qb-4*qa*qc);q=-.5*(qb+math.copysign(delta,qb))
   ts=[q/qa,qc/q];pts=[(f+t*dx,t*dy) for t in ts];rs=[abs(t) for t in ts]
   for (x,y),r in zip(pts,rs):
    eq(x*x/a**2-y*y/b**2,1);eq(math.hypot(x-f,y),r)
    eq(r,abs(sign*e*x-a))
   signed=[sign*e*x-a for x,y in pts];eq(sum(1/u for u in signed),K)
   if pts[0][0]*pts[1][0]>0:
    assert ts[0]*ts[1]<0 and all(sign*x>0 for x,y in pts)
    eq(1/rs[0]+1/rs[1],K)
    assert all(r>p/2 for r in rs)
    eq((pts[0][0]-f)/rs[0],-(pts[1][0]-f)/rs[1]);same+=1
   else:
    assert ts[0]*ts[1]>0
    near=next(i for i,(x,y) in enumerate(pts) if sign*x>0);far=1-near
    assert rs[near]<rs[far]
    eq(1/rs[near]-1/rs[far],K)
    eq((pts[0][0]-f)/rs[0],(pts[1][0]-f)/rs[1]);cross+=1
   two+=1
  # Exact asymptote directions: the quadratic term vanishes, one finite root remains.
  for k in [b/a,-b/a]:
   x=(a*a*(c*c*k*k+b*b))/(2*a*a*f*k*k)
   y=k*(x-f);eq(x*x/a**2-y*y/b**2,1)

# Pure geometry, same/opposite rays.
P=(0,0)
for A,B,opposite in [((1.2,1.6),(-.6,-.8),True),((-.6,.8),(-1.8,2.4),False)]:
 r,s=math.dist(P,A),math.dist(P,B)
 eq(A[0]/r,(-1 if opposite else 1)*B[0]/s)
 eq(math.dist(A,B),r+s if opposite else s-r)

# Example and diagram checks, independent Cartesian substitution and distances.
for a,b,F,A,B,r,s in [
 (3,4,(5,0),(33/5,16*math.sqrt(6)/5),(21/5,-8*math.sqrt(6)/5),8,4),
 (2,4,(2*math.sqrt(5),0),(math.sqrt(5),2),(-2*math.sqrt(5),8),3,12),
 (3,4,(5,0),(18/5,4*math.sqrt(11)/5),(81/5,-32*math.sqrt(11)/5),3,24)]:
 for x,y in [A,B]:eq(x*x/a**2-y*y/b**2,1)
 eq(math.dist(F,A),r);eq(math.dist(F,B),s)
 eq((A[0]-F[0])*(B[1]-F[1]),(B[0]-F[0])*(A[1]-F[1]))
 if A[0]*B[0]>0:eq(1/r+1/s,2*a/b**2)
 else:eq(1/r-1/s,2*a/b**2)
eq(1/3+1/24,3/8);eq(1/3-1/12,1/4)
eq((16*math.sqrt(6)/5)/(33/5-5),2*math.sqrt(6))
eq(3/8-1/2,-1/8);eq(3/8-1/(8/3),0)
eq(1/2-1/8,3/8) # Actual horizontal chord of example 4 is cross-branch.
x,y=17/5,-32/15;eq(x*x/9-y*y/16,1);eq(y,4/3*(x-5));eq(math.hypot(x-5,y),8/3)
# Reciprocal bar dimensions are proportional to the claimed reciprocal values.
eq(1.4/2.8,(1/8)/(1/4));eq(1.2/4.8,(1/12)/(1/3));eq((16/3)/(2/3),(1/3)/(1/24))
base=Path('03_conic/C057_hyperbola_focus_chord_reciprocal_sum_diff')
json.loads((base/'meta.json').read_text(encoding='utf8'))
for stem in ['statement_comparison','pure_positions','pure_projection','same_branch_sum','cross_branch_difference','reciprocal_feasibility','intersection_boundary']:
 txt=Path(f'assets/tikz/C057_{stem}.tex').read_text(encoding='utf8');assert '\\tiny' not in txt and '\\scriptsize' not in txt
for name in ['main.tex','source.tex']:
 assert (base/name).read_bytes()==(Path('.tmp/C057_tikz_review/before')/name).read_bytes()
proof=(base/'03_proof.tex').read_text(encoding='utf8')
for marker in ['证明一','证明二','证明三','先证一个']:assert marker in proof
ex=(base/'04_examples.tex').read_text(encoding='utf8')
for i in range(1,6):assert f'例{i}' in ex
result={'status':'PASS','two_finite_intersection_states':two,'same_branch_states':same,'cross_branch_states':cross,'sampled_single_intersection_states':one,'additional_exact_asymptote_checks':16,'models_a_b':models,'focus_choices':2,'angles_degrees':'0..179','figures':7,'examples':5,'main_source_preserved':True}
Path('.tmp/C057_tikz_review/math_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
