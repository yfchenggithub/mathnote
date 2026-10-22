"""Independent C035 numerical audit; finite cases cross-check the general proofs."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import re,math,json
ROOT=Path(__file__).resolve().parents[3]
UID=ROOT/'03_conic/C035_parabola_vieta_fixed_form'
def close(a,b):
 assert math.isclose(a,b,rel_tol=2e-7,abs_tol=2e-7),(a,b)
def on(P,p,s,A,B,C,vertical):
 x,y=P
 close(x*x if vertical else y*y,2*s*p*(y if vertical else x))
 close(A*x+B*y+C,0)
def expected(p,s,A,B,C,v):
 if v:
  D=p*p*A*A-2*s*p*B*C
  return (-2*s*p*A/B,2*s*p*C/B,(2*s*p*A*A-2*B*C)/(B*B),C*C/(B*B),D)
 D=p*p*B*B-2*s*p*A*C
 return ((2*s*p*B*B-2*A*C)/(A*A),C*C/(A*A),-2*s*p*B/A,2*s*p*C/A,D)
def case(p,s,A,B,C,v):
 # Parameterize the line with Euclidean foot plus t(B,-A); do not use Vieta to get points.
 norm=A*A+B*B
 x0,y0=-F(A*C,norm),-F(B*C,norm)
 if v:q=F(B*B);r=2*B*x0+2*s*p*A;u=x0*x0-2*s*p*y0
 else:q=F(A*A);r=-2*A*y0-2*s*p*B;u=y0*y0-2*s*p*x0
 if q==0:
  assert r!=0
  t=-u/r;P=(float(x0+t*B),float(y0-t*A))
  on(P,p,s,A,B,C,v)
  if v:close(P[0],-C/A);close(P[1],s*C*C/(2*p*A*A))
  else:close(P[0],s*C*C/(2*p*B*B));close(P[1],-C/B)
  return 'axis-one'
 xs,xp,ys,yp,H=expected(p,s,A,B,C,v)
 delta=r*r-4*q*u
 assert delta==4*H
 # Verify coefficients of the secondary projection equation and its discriminant, even if there are no real points.
 if v:
  qa=F(B*B);qb=2*B*C-2*s*p*A*A;qc=F(C*C)
  assert qb*qb-4*qa*qc==4*A*A*H
 else:
  qa=F(A*A);qb=2*A*C-2*s*p*B*B;qc=F(C*C)
  assert qb*qb-4*qa*qc==4*B*B*H
 if H<0:return 'no-real'
 ts=[(-float(r)+k*math.sqrt(float(delta)))/(2*float(q)) for k in [-1,1]]
 P,Q=[(float(x0)+t*B,float(y0)-t*A) for t in ts]
 on(P,p,s,A,B,C,v);on(Q,p,s,A,B,C,v)
 close(P[0]+Q[0],xs);close(P[0]*Q[0],xp)
 close(P[1]+Q[1],ys);close(P[1]*Q[1],yp)
 den=B*B if v else A*A
 L=2*math.sqrt(float(norm*H))/den
 close(math.dist(P,Q),L)
 if v:
  close((P[0]+Q[0])/2,-s*p*A/B)
  close((P[1]+Q[1])/2,(s*p*A*A-B*C)/(B*B))
 else:
  close((P[0]+Q[0])/2,(s*p*B*B-A*C)/(A*A))
  close((P[1]+Q[1])/2,-s*p*B/A)
 # Same geometric line after coefficient rescaling; compare all coordinate relations and length.
 for lam in [-3,2]:
  out=expected(p,s,lam*A,lam*B,lam*C,v)
  for a,b in zip(out[:4],[xs,xp,ys,yp]):close(a,b)
  close(2*math.sqrt(float(lam*lam*norm*out[4]))/(lam*lam*den),L)
 return 'tangent' if H==0 else 'two-real'
def figures():
 # Each tuple describes one chart: p, opening sign, A, B, C, vertical opening.
 models={
 'roots_projection':[(2,1,1,1,-2,False)],
 'intersection_states':[(2,1,1,0,-1,False)],
 'axis_parallel':[(2,1,0,1,-1,False),(2,1,1,0,0,False)],
 'reflection':[(2,1,1,0,-1,False),(2,-1,1,0,1,False)],
 'coordinate_swap':[(2,1,1,0,-1,False),(2,1,0,1,-1,True)],
 'squaring_sign':[(2,1,1,-1,-1,False)],
 'chord_midpoint':[(2,1,1,1,-2,False)],
 'midpoint_example':[(4,1,2,-1,1,True)],
 'tangent_candidate':[(2,1,-2,-1,1,False)]}
 paths=list((ROOT/'assets/tikz').glob('C035_*.tex'));assert len(paths)==len(models)
 for name,mods in models.items():
  text=(ROOT/f'assets/tikz/C035_{name}.tex').read_text(encoding='utf-8')
  charts=re.split(r'\\begin\{scope\}\[shift=',text)[1:];assert len(charts)==len(mods)
  for chart,(p,s,A,B,C,v) in zip(charts,mods):
   # Validate the actual plot expression, not the model comment.
   pat=r'plot \(\\t,\{\\t\*\\t/\((-?[\d.]+)\)\}\)' if v else r'plot \(\{\\t\*\\t/\((-?[\d.]+)\)\},\\t\)'
   curves=re.findall(pat,chart);assert len(curves)==1,(name,curves)
   close(float(curves[0]),2*s*p)
   pts={n:(float(x),float(y)) for n,x,y in re.findall(r'\\coordinate \(([^)]+)\) at \(([-\d.]+),([-\d.]+)\);',chart)}
   clip=re.search(r'\\clip \(([-\d.]+),([-\d.]+)\) rectangle \(([-\d.]+),([-\d.]+)\);',chart)
   assert clip
   xmin,ymin,xmax,ymax=map(float,clip.groups())
   for n,P in pts.items():
    assert xmin-1e-8<=P[0]<=xmax+1e-8 and ymin-1e-8<=P[1]<=ymax+1e-8,(name,n,P)
    if n=='S' or (name=='chord_midpoint' and n=='T'):continue
    if name=='intersection_states' and n=='T':on(P,p,s,1,0,0,v)
    elif name=='tangent_candidate' and n=='T':on(P,p,s,1,-1,1,v)
    else:on(P,p,s,A,B,C,v)
   for x,y,xx,yy in re.findall(r'\\draw\[orange[^\]]*\] \(([-\d.]+),([-\d.]+)\)--\(([-\d.]+),([-\d.]+)\);',chart):
    close(A*float(x)+B*float(y)+C,0);close(A*float(xx)+B*float(yy)+C,0)
   if 'S' in pts:
    P,Q,S=pts['P'],pts['Q'],pts['S']
    close(S[0],(P[0]+Q[0])/2);close(S[1],(P[1]+Q[1])/2)
    close(A*S[0]+B*S[1]+C,0)
   if name=='chord_midpoint':
    P,Q,T=pts['P'],pts['Q'],pts['T']
    close(T[0],Q[0]);close(T[1],P[1])
    mark=re.search(r'\\draw \(([-\d.]+),([-\d.]+)\)--\(([-\d.]+),([-\d.]+)\)--\(([-\d.]+),([-\d.]+)\);',chart)
    assert mark
    x,y,xx,yy,xxx,yyy=map(float,mark.groups())
    close(x,xx);close(yy,yyy);close(xxx,T[0]);close(y,T[1]);close(T[0]-x,T[1]-yy)
    close(math.dist(P,Q),4*math.sqrt(6))
   if name=='squaring_sign':
    raw=re.findall(r'\\fill\[black\] \(([-\d.]+),([-\d.]+)\) circle',chart);assert len(raw)==4
    for x,y in raw:
     x,y=float(x),float(y);close(y*y,4*x);close((x-1)**2,4*x)
     assert math.isclose(y,x-1,abs_tol=1e-8) or math.isclose(y,1-x,abs_tol=1e-8)
   if name=='tangent_candidate':
    close(pts['S'][0],1);close(pts['S'][1],-1);close(pts['T'][0],1);close(pts['T'][1],2)
 meta=json.loads((UID/'meta.json').read_text(encoding='utf-8'))
 assert meta['interactive']['has_diagram'] and meta['meta']['updated_at']=='2026-10-22'
 for path in paths:assert path.relative_to(ROOT).as_posix() in meta['remarks']
 for uid in meta['relations']['related_ids']:assert any((ROOT/'03_conic').glob(uid+'_*'))
 return len(paths)
def main():
 counts=Counter()
 for p in [F(1,2),F(1),F(2),F(4)]:
  for s in [-1,1]:
   for v in [False,True]:
    for A in range(-3,4):
     for B in range(-3,4):
      if not A and not B:continue
      for C in range(-4,5):counts[case(p,s,A,B,C,v)]+=1
 n=figures()
 # Explicit false-projection regression: x=-1 is a double algebraic root but there is no real point.
 assert case(F(2),1,1,0,1,False)=='no-real'
 # Independent example checks.
 close(math.sqrt(5)*math.sqrt(64+32),4*math.sqrt(30))
 close((8+6*math.sqrt(2))+(8-6*math.sqrt(2)),16)
 for k in [1,-2]:assert k*k+k-2==0
 assert 4-4*1==0 and 4-4*(-2)>0
 print(f'PASS: {sum(counts.values())} cases {dict(counts)}; {n} actual TikZ models; real-point classification, false projection, Vieta, midpoint, chord, scaling, examples and metadata.')
if __name__=='__main__':main()
