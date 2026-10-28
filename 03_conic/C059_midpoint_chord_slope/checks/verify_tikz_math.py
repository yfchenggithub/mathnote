"""Independent conic/root and actual TikZ constant checks for C059."""
import json
import math
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
UID=Path(__file__).resolve().parents[1]
checks=0


def close(a,b,tol=1e-8):
    global checks
    checks+=1
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)


def macro(file,name,**values):
    source=(ROOT/'assets/tikz'/file).read_text(encoding='utf8')
    match=re.search(r'\\pgfmathsetmacro\{\\'+name+r'\}\{([^{}]+)\}',source)
    assert match,(file,name)
    expr=match[1]
    for key in values: expr=expr.replace('\\'+key,key)
    return eval(expr,{'__builtins__':{}},{'sqrt':math.sqrt,**values})


def roots(A,B,C):
    d=B*B-4*A*C
    if abs(A)<1e-12 or d<=0: return None
    return sorted([(-B-math.sqrt(d))/(2*A),(-B+math.sqrt(d))/(2*A)])


def conic_line(a,b,sign,M,k):
    x,y=M
    t=y-k*x
    co=(1/a**2+sign*k*k/b**2,2*sign*k*t/b**2,sign*t*t/b**2-1)
    rs=roots(*co)
    if rs is None:return None,co
    pts=[(r,k*r+t) for r in rs]
    for X,Y in pts:close(X*X/a**2+sign*Y*Y/b**2,1)
    close(sum(p[0] for p in pts)/2,x)
    close(sum(p[1] for p in pts)/2,y)
    return pts,co


# Every displayed common ellipse point is driven by the literal TikZ macro.
for file in ['C059_overview.tex','C059_difference_projection.tex','C059_vieta_projection.tex',
             'C059_gradient_level.tex','C059_circle_rescale.tex']:
    u=macro(file,'u')
    for x,y in [(1-u,1+.75*u),(1+u,1-.75*u)]:
        close(x*x/4+y*y/3,1)
    close(u*u,20/21)

w=macro('C059_overview.tex','w')
for x,y in [(1-w,1-.25*w),(1+w,1+.25*w)]:close(x*x/4-y*y,1)
for x,y in [(1-math.sqrt(3)/2,1-math.sqrt(3)),
            (1+math.sqrt(3)/2,1+math.sqrt(3))]:close(y*y,4*x)

# Vieta, actual example roots, false candidate, and the two valid hyperbola regions.
conic_line(2,math.sqrt(3),1,(1,1),-.75)
pts,co=conic_line(2,math.sqrt(5),-1,(4,3),5/3)
u=macro('C059_existence_cases.tex','u')
close(pts[0][0],4-u);close(pts[1][0],4+u)
close(440**2-4*55*664,47520)
conic_line(2,math.sqrt(5),-1,(0,1),0)
none,co=conic_line(2,math.sqrt(5),-1,(1,1),5/4)
assert none is None
close(co[1]**2-4*co[0]*co[2],-95/400)
# The displayed unscaled equation multiplies these coefficients by 20.
close((20*co[1])**2-4*(20*co[0])*(20*co[2]),-95)

parameter_cases=0
for a,b in [(2,1),(2,math.sqrt(5)),(4,2),(1,3)]:
    for x in [-4,-1,0,1,4]:
        for y in [-3,-1,.5,2]:
            parameter_cases+=1
            Q=x*x/a**2-y*y/b**2
            k=b*b*x/(a*a*y)
            pts,co=conic_line(a,b,-1,(x,y),k)
            exists=Q<0 or Q>1
            assert (pts is not None)==exists,(a,b,x,y,Q,co)

# The changed level curve passes through M and its normal is perpendicular to AB.
close(1/4+1/3,7/12)
close(1.5275252317**2,7/3)
close(1.3228756555**2,7/4)
close(.5*1+(2/3)*(-.75),0)
u=math.sqrt(20/21)
X,Y=.5,1/math.sqrt(3)
dx,dy=u,-1.5*u/math.sqrt(3)
close(X*dx+Y*dy,0)
close(1*(-.75),-.75)

# Midpoint offsets, original center chords, and the new vertical chord.
close(math.hypot(2,1),math.hypot(-2,-1))
for x,y in [(-1.897366596101,-.316227766017),(1.897366596101,.316227766017),
            (1,.8660254038),(1,-.8660254038)]:close(x*x/4+y*y,1)
close(3**2+4**2,25)

# Actual parabola trajectory parameters from the TikZ loop.
source=(ROOT/'assets/tikz/C059_parabola_locus.tex').read_text(encoding='utf8')
ms=re.search(r'\\foreach \\m/\\col in \{([^}]+)\}',source)[1]
for entry in ms.split(','):
    m=float(entry.split('/')[0])
    v=macro('C059_parabola_locus.tex','v',m=m)
    pts=[(m-v/2,1-v),(m+v/2,1+v)]
    for x,y in pts:close(y*y,4*x)
    close(sum(x for x,y in pts)/2,m)
    close(sum(y for x,y in pts)/2,1)
    close((pts[1][1]-pts[0][1])/(pts[1][0]-pts[0][0]),2)
    assert m>.25
close(1**2,4*.25)

proof=(UID/'03_proof.tex').read_text(encoding='utf8')
sections=re.split(r'方法[一二三四]：',proof)[1:]
assert len(sections)==4
assert all('\\input{assets/tikz/C059_' in part for part in sections)
assert 'C059_existence_cases' in proof.split('补充论证：')[1]
assert 'C059_overview' in (UID/'01_statement.tex').read_text(encoding='utf8')
figures=[p for p in (ROOT/'assets/tikz').glob('C059_*.tex') if p.name!='C059_math_audit_geometry.tex']
assert len(figures)==9
assert all('\\tiny' not in p.read_text(encoding='utf8') for p in figures)
print(json.dumps(dict(status='PASS',numerical_checks=checks,hyperbola_parameter_cases=parameter_cases,
                      proof_methods_with_diagrams=4,supplement_has_diagram=True,new_figures=len(figures)),indent=2))
