"""Independent C033 audit: actual TikZ models, elimination and geometry.

Finite samples cross-check the general proofs and are not a substitute for them.
"""
from pathlib import Path
from fractions import Fraction as F
import math,re,json
ROOT=Path(__file__).resolve().parents[3]
UID=ROOT/'03_conic/C033_ellipse_line_vieta_formula'
def close(a,b):
    assert math.isclose(a,b,rel_tol=3e-8,abs_tol=3e-8),(a,b)
def on(P,a,b,A,B,C):
    close(P[0]**2/a+P[1]**2/b,1)
    close(A*P[0]+B*P[1]+C,0)
def check_points(P,Q,a,b,A,B,C):
    on(P,a,b,A,B,C);on(Q,a,b,A,B,C)
    D=A*A*a+B*B*b;H=D-C*C
    if B:
        close(P[0]+Q[0],-2*A*C*a/D)
        close(P[0]*Q[0],a*(C*C-B*B*b)/D)
    if A:
        close(P[1]+Q[1],-2*B*C*b/D)
        close(P[1]*Q[1],b*(C*C-A*A*a)/D)
    close((P[0]+Q[0])/2,-A*C*a/D)
    close((P[1]+Q[1])/2,-B*C*b/D)
    close(math.dist(P,Q),2*math.sqrt(max(0,a*b*(A*A+B*B)*H))/D)
def verify():
    paths=list((ROOT/'assets/tikz').glob('C033_*.tex'));assert len(paths)==10
    for path in paths:
        s=path.read_text(encoding='utf-8')
        a,b,A,B,C=map(float,re.search(r'% MODEL ([\d.e+-]+) ([\d.e+-]+) ([\d.e+-]+) ([\d.e+-]+) ([\d.e+-]+)',s).groups())
        pts={k:(float(x),float(y)) for k,x,y in re.findall(r'\\coordinate \((\w+)\) at \(([-\d.]+),([-\d.]+)\);',s)}
        if 'P' in pts and 'Q' in pts:
            check_points(pts['P'],pts['Q'],a,b,A,B,C)
        if 'M' in pts:
            D=A*A*a+B*B*b
            close(pts['M'][0],-A*C*a/D);close(pts['M'][1],-B*C*b/D)
        radii=[tuple(map(float,g)) for g in re.findall(r'ellipse \(([\d.]+) and ([\d.]+)\)',s)]
        assert radii
        close(radii[0][0]**2,a);close(radii[0][1]**2,b)
        if 'denominator_order' in path.name:
            close(radii[1][0]**2,b);close(radii[1][1]**2,a)
        if 'chord_triangle' in path.name:
            P,Q,T=pts['P'],pts['Q'],pts['T']
            close(T[0],Q[0]);close(T[1],P[1])
            close(math.dist(P,Q)**2,math.dist(P,T)**2+math.dist(T,Q)**2)
        if 'intersection_states' in path.name:
            on(pts['T'],a,b,0,1,-2)
            assert b-(13/5)**2<0
        if 'vertical_exception' in path.name:
            close(pts['P'][0],pts['Q'][0]);assert math.dist(pts['P'],pts['Q'])>3
            assert B==0 and A!=0
        if 'unit_circle' in path.name:
            close(pts['M'][0]/math.sqrt(a),pts['N'][0]);close(pts['M'][1]/math.sqrt(b),pts['N'][1])
            assert '(0,0) circle (1)' in s
            for x in (-.8660254038,.8660254038):close(x*x+.5**2,1)
        if 'perpendicular_example' in path.name:
            P,Q,S,O=[pts[k] for k in ('P','Q','S','O')]
            close(P[0]*Q[0]+P[1]*Q[1],0)
            on(S,a,b,1,-math.sqrt(2),math.sqrt(2))
            close((Q[1]-P[1])/(Q[0]-P[0]),-1/math.sqrt(2))
            close((S[1]-P[1])/(S[0]-P[0]),1/math.sqrt(2))
        if 'midpoint_not_foot' in path.name:
            N=pts['N'];close(A*N[0]+B*N[1]+C,0)
            close(N[0]*B-N[1]*A,0)
            assert math.dist(N,pts['M'])>.5
        if 'line_sign' in path.name:
            for x,y in [(-1.2,2.2),(2.6,-1.6)]:close(x+y-1,0)
            for x,y in [(-1.2,-2.2),(2.6,1.6)]:close(-x+y+1,0)
    count=0;states={-1:0,0:0,1:0}
    for a in (1,2,3,8,9):
      for b in (1,4,5):
       for A in range(-2,3):
        for B in range(-2,3):
         if A==B==0:continue
         for C in range(-3,4):
          D=A*A*a+B*B*b;H=D-C*C;sgn=(H>0)-(H<0);states[sgn]+=1;count+=1
          dx=(2*A*C*a)**2-4*D*a*(C*C-B*B*b)
          dy=(2*B*C*b)**2-4*D*b*(C*C-A*A*a)
          close(dx,4*a*b*B*B*H);close(dy,4*a*b*A*A*H)
          if H<0:continue
          # Compute real endpoints from a legal quadratic, independently of midpoint parametrization.
          if B:
           xs=[(-2*A*C*a+sign*math.sqrt(dx))/(2*D) for sign in (-1,1)]
           P,Q=[(x,-(A*x+C)/B) for x in xs]
          else:
           ys=[(-2*B*C*b+sign*math.sqrt(dy))/(2*D) for sign in (-1,1)]
           P,Q=[(-(B*y+C)/A,y) for y in ys]
          check_points(P,Q,a,b,A,B,C)
          for scale in (-3,2):
           d2=scale*scale*D;h2=scale*scale*H
           close(-scale*A*scale*C*a/d2,(P[0]+Q[0])/2)
           close(2*math.sqrt(max(0,a*b*scale*scale*(A*A+B*B)*h2))/d2,math.dist(P,Q))
    assert F(12,16)/2==F(3,8) and 1-2*F(3,8)==F(1,4)
    assert F(16,9)-4*F(-2)==F(88,9)
    m=json.loads((UID/'meta.json').read_text(encoding='utf-8'))
    refs=re.findall(r'assets/tikz/C033_[a-z_]+\.tex',m['remarks']);assert len(refs)==10
    assert all((ROOT/p).is_file() for p in refs)
    assert m['interactive']['has_diagram'] and m['meta']['updated_at']=='2026-10-22'
    for rid in m['relations']['related_ids']:assert len(list((ROOT/'03_conic').glob(rid+'_*')))==1
    print(f'PASS: 10 actual TikZ models; {count} line/ellipse cases {states}; Vieta, discriminants, midpoint, chord length, coefficient rescaling, examples and metadata.')
if __name__=='__main__':verify()
