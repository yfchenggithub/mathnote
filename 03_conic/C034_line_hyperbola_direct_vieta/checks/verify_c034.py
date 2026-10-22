"""C034 independent cross-checks; finite sampling does not replace the proofs."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import math, re, json
ROOT=Path(__file__).resolve().parents[3]
UID=ROOT/'03_conic/C034_line_hyperbola_direct_vieta'
def close(a,b):
    assert math.isclose(a,b,rel_tol=2e-7,abs_tol=2e-7),(a,b)
def on(P,aa,bb,A,B,C,vertical=False):
    x,y=P
    close(y*y/aa-x*x/bb if vertical else x*x/aa-y*y/bb,1)
    close(A*x+B*y+C,0)
def verify_formula(aa,bb,A,B,C,vertical):
    sx,sy=(-F(1,bb),F(1,aa)) if vertical else (F(1,aa),-F(1,bb))
    # Independently parameterize the line from its Euclidean perpendicular foot.
    norm=A*A+B*B
    x0,y0=-F(C*A,norm),-F(C*B,norm)
    q=sx*B*B+sy*A*A
    r=2*(sx*x0*B-sy*y0*A)
    s=sx*x0*x0+sy*y0*y0-1
    D=bb*A*A-aa*B*B if vertical else bb*B*B-aa*A*A
    H=C*C+D
    assert q==F(D,aa*bb)
    if not q:
        assert A and B
        if C==0:
            assert r==0 and s!=0
            return 'asymptote'
        assert r!=0
        t=-s/r
        on((float(x0+t*B),float(y0-t*A)),aa,bb,A,B,C,vertical)
        return 'linear-one'
    delta=r*r-4*q*s
    assert (delta>0)-(delta<0)==(H>0)-(H<0)
    # Direct substitution coefficients, independently constructed from the conic.
    if B:
        px=sx+sy*F(A*A,B*B);qx=2*sy*F(A*C,B*B);rx=sy*F(C*C,B*B)-1
        close(float(qx*qx-4*px*rx)*B**4*aa**2*bb**2,4*aa*bb*B*B*H)
    if A:
        py=sy+sx*F(B*B,A*A);qy=2*sx*F(B*C,A*A);ry=sx*F(C*C,A*A)-1
        close(float(qy*qy-4*py*ry)*A**4*aa**2*bb**2,4*aa*bb*A*A*H)
    if delta<0:return 'no-real'
    ts=[(-float(r)+sgn*math.sqrt(float(delta)))/(2*float(q)) for sgn in [-1,1]]
    P,Q=[(float(x0)+t*B,float(y0)-t*A) for t in ts]
    on(P,aa,bb,A,B,C,vertical);on(Q,aa,bb,A,B,C,vertical)
    if vertical:
        xs=-2*A*C*bb/D;xp=bb*(C*C-B*B*aa)/D
        ys=2*B*C*aa/D;yp=-aa*(C*C+A*A*bb)/D
    else:
        xs=2*A*C*aa/D;xp=-aa*(C*C+B*B*bb)/D
        ys=-2*B*C*bb/D;yp=bb*(C*C-A*A*aa)/D
    # Even an illegal projection can have correct numerical sums; do not use it to count points.
    close(P[0]+Q[0],xs);close(P[0]*Q[0],xp)
    close(P[1]+Q[1],ys);close(P[1]*Q[1],yp)
    close(math.dist(P,Q),2*math.sqrt(aa*bb*norm*H)/abs(D))
    # Independent root-difference / coefficient scaling check in legal direction.
    if B:
        de=float(qx*qx-4*px*rx)
        for lam in [-3,2]:close(math.sqrt(max(0,de*lam*lam))/abs(float(px)*lam),abs(P[0]-Q[0]))
    return 'tangent' if delta==0 else 'two-real'
def verify_figures():
    # (semi-axis squares, line coefficients, vertical flag), one entry per chart scope.
    models={
      'roots_projection':[(4,1,1,-1,2,False)],
      'intersection_states':[(2,1,1,-1,2,False)],
      'asymptote_parallel':[(1,1,1,-1,1,False)],
      'one_point_not_tangent':[(1,1,1,-1,1,False),(1,1,1,0,-1,False)],
      'coordinate_swap':[(4,1,1,-1,2,False),(4,1,-1,1,2,True)],
      'chord_triangle':[(4,1,1,-1,2,False)],
      'vertical_hyperbola_example':[(5,4,2,-1,1,True)],
      'parameter_symmetry':[(2,1,1,-1,2,False)],
      'vertical_chord':[(4,1,1,0,-3,False)]}
    paths=list((ROOT/'assets/tikz').glob('C034_*.tex'));assert len(paths)==len(models)
    for name,mods in models.items():
        text=(ROOT/f'assets/tikz/C034_{name}.tex').read_text(encoding='utf-8')
        charts=re.split(r'\\begin\{scope\}\[shift=',text)[1:]
        assert len(charts)==len(mods)
        for chart,(aa,bb,A,B,C,v) in zip(charts,mods):
            pts={n:(float(x),float(y)) for n,x,y in re.findall(r'\\coordinate \(([^)]+)\) at \(([-\d.]+),([-\d.]+)\);',chart)}
            for n,P in pts.items():
                if name=='chord_triangle' and n=='T':continue
                if name=='intersection_states' and n=='T':cc=1
                elif name=='parameter_symmetry' and "'" in n:cc=-2
                else:cc=C
                on(P,aa,bb,A,B,cc,v)
            # Validate the actual curve parameters, not just copied model comments.
            pattern=r'plot \(\\t,\{(-?[\d.]+)\*sqrt\(1\+\(\\t/([\d.]+)\)\^2\)\}\)' if v else r'plot \(\{(-?[\d.]+)\*sqrt\(1\+\(\\t/([\d.]+)\)\^2\)\},\\t\)'
            curves=re.findall(pattern,chart);assert len(curves)==2,(name,curves)
            for a,b in curves:close(float(a)**2,aa);close(float(b)**2,bb)
            lines=re.findall(r'\\draw\[orange[^\]]*\] \(([-\d.]+),([-\d.]+)\)--\(([-\d.]+),([-\d.]+)\);',chart)
            for x,y,xx,yy in lines:
                close(A*float(x)+B*float(y)+C,0);close(A*float(xx)+B*float(yy)+C,0)
            if name=='chord_triangle':
                P,Q,T=pts['P'],pts['Q'],pts['T']
                close(T[0],Q[0]);close(T[1],P[1]);close(math.dist(P,Q),4*math.sqrt(2)/3)
                mark=re.search(r'\\draw \(([-\d.]+),([-\d.]+)\)--\(([-\d.]+),([-\d.]+)\)--\(([-\d.]+),([-\d.]+)\);',chart)
                assert mark
                x,y,xx,yy,xxx,yyy=map(float,mark.groups())
                close(x,xx);close(yy,yyy);close(xxx,T[0]);close(y,T[1]);close(T[0]-x,yy-T[1])
            if name=='vertical_chord':close(math.dist(pts['P'],pts['Q']),math.sqrt(5))
    meta=json.loads((UID/'meta.json').read_text(encoding='utf-8'))
    assert meta['interactive']['has_diagram'] is True
    assert meta['meta']['updated_at']=='2026-10-22'
    for path in paths:assert path.relative_to(ROOT).as_posix() in meta['remarks']
    for uid in meta['relations']['related_ids']:assert any((ROOT/'03_conic').glob(uid+'_*'))
    return len(paths)
def main():
    counts=Counter()
    for vertical in [False,True]:
      for aa in [1,2,4,9]:
       for bb in [1,4,5]:
        for A in range(-2,3):
         for B in range(-2,3):
          if not A and not B:continue
          for C in range(-3,4):counts[verify_formula(aa,bb,A,B,C,vertical)]+=1
    n=verify_figures()
    # Three examples have independent reduced polynomials / exact answers.
    assert F(-16,3)**2-4*F(20,3)==F(16,9)
    assert 4*F(-16,11)+2*F(-16,11)+1==F(-85,11)
    for m in [-2,2]:close(4*math.sqrt(m*m-1),4*math.sqrt(3))
    print(f'PASS: {sum(counts.values())} cases {dict(counts)}; {n} actual TikZ models; Vieta, discriminants, degeneration, midpoint, length, scaling, examples and metadata.')
if __name__=='__main__':main()
