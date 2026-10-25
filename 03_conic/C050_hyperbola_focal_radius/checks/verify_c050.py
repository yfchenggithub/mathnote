"""Independent Euclidean audit of C050 and the actual teaching figures."""
from pathlib import Path
import json
import math
import re

ROOT=Path(__file__).resolve().parents[3]
UID=Path(__file__).resolve().parents[1]
def close(x,y):
    assert math.isclose(x,y,rel_tol=2e-9,abs_tol=2e-9),(x,y)
def verify(a,b,p):
    x,y=p;c=math.hypot(a,b);e=c/a
    close(x*x/(a*a)-y*y/(b*b),1)
    d1=math.hypot(x+c,y);d2=math.hypot(x-c,y)
    close(d1,abs(a+e*x));close(d2,abs(a-e*x))
    close(abs(d1-d2),2*a);close(d1+d2,2*e*abs(x))
    close(d1*d1-d2*d2,4*c*x)
    t=(d1+d2)/2;close(t,e*abs(x))
    close(min(d1,d2),t-a);close(max(d1,d2),t+a)
    assert t>=c-1e-10 and min(d1,d2)>0
    if x>0:
        assert d1>d2 and a+e*x>0 and a-e*x<0
        close(d1,e*x+a);close(d2,e*x-a)
    else:
        assert d1<d2 and a+e*x<0 and a-e*x>0
        close(d1,-e*x-a);close(d2,-e*x+a)
    ell=a/e
    assert -a < -ell < ell < a
    close(d1,e*abs(x+ell));close(d2,e*abs(x-ell))
    # Reflection in the focus axis and a 90-degree rotation preserve distance.
    close(math.hypot(x+c,-y),d1);close(math.hypot(x-c,-y),d2)
    xp,yp=-y,x
    close(math.hypot(xp,yp+c),abs(a+e*yp))
    close(math.hypot(xp,yp-c),abs(a-e*yp))
    return d1,d2

states=0
for a,b in [(2,math.sqrt(5)),(4,3),(3,4),(1,.25),(1,4)]:
    for n in range(41):
        u=n*.065
        for sx in [-1,1]:
            for sy in [-1,1]:
                verify(a,b,(sx*a*math.cosh(u),sy*b*math.sinh(u)));states+=1

# Actual main/branch/rotated figure coordinates.
for p,target in [((3,2.5),(6.5,2.5)),((-3,2.5),(2.5,6.5))]:
    for v,w in zip(verify(2,math.sqrt(5),p),target):close(v,w)
# The six original examples, including the inverse problem's vertex.
for a,b,p,target in [
    (4,3,(5,9/4),(41/4,9/4)),
    (5,math.sqrt(39),(5,0),(13,3)),
    (4,3,(32/5,3*math.sqrt(39)/5),(12,4)),
    (3,4,(-6,4*math.sqrt(3)),(7,13)),
    (4,3,(-8,3*math.sqrt(3)),(6,14)),
]:
    for v,w in zip(verify(a,b,p),target):close(v,w)
for sx in [-1,1]:
    ds=verify(4,3,(sx*4,0))
    close(ds[0],9 if sx==1 else 1);close(ds[1],1 if sx==1 else 9)

for suffix in ['math_audit_geometry','branch_comparison','directrix_geometry','focus_axis_comparison']:
    text=(ROOT/'assets/tikz'/f'C050_{suffix}.tex').read_text(encoding='utf-8')
    assert r'\coordinate (P) at (3,2.5);' in text
    assert r'1+\z*\z/5' in text
assert r'\coordinate (P) at (-3,2.5);' in (ROOT/'assets/tikz/C050_branch_comparison.tex').read_text(encoding='utf-8')
assert r'\coordinate (P) at (-2.5,3);' in (ROOT/'assets/tikz/C050_focus_axis_comparison.tex').read_text(encoding='utf-8')
# Aligned bars are literal lengths at scale 1.5 cm per unit.
source=(ROOT/'assets/tikz/C050_mean_length_segments.tex').read_text(encoding='utf-8')
assert '(2,6.0) rectangle (11.75,6.2)' in source
assert '(2,4.6)--(8.75,4.6)' in source
assert '(2,2.9) rectangle (5.75,3.1)' in source
close((11.75-2)/1.5,6.5);close((8.75-2)/1.5,4.5);close((5.75-2)/1.5,2.5)
source=(ROOT/'assets/tikz/C050_branch_comparison.tex').read_text(encoding='utf-8')
for color,targets in [('blue!45',[2.5,6.5]),('orange!50',[6.5,2.5])]:
    pattern=r'\\fill\['+re.escape(color)+r'\] \(([-\d.]+),[-\d.]+\) rectangle \(([-\d.]+),[-\d.]+\);'
    matches=re.findall(pattern,source)
    assert len(matches)==2
    for (x1,x2),target in zip(matches,targets):close((float(x2)-float(x1))/.5,target)
for tex in UID.glob('0[1-6]_*.tex'):
    for name in re.findall(r'\\input\{([^}]+)\}',tex.read_text(encoding='utf-8')):
        assert (ROOT/(name if name.endswith('.tex') else name+'.tex')).is_file(),name
d=json.loads((UID/'meta.json').read_text(encoding='utf-8'))
assert d['id']=='C050' and d['interactive']['has_diagram'] is True
print(f'C050 PASS: {states} states; both branches, both half-planes, vertices, absolute-value signs, directrices, aligned actual lengths, rotations, six examples and TeX references.')
