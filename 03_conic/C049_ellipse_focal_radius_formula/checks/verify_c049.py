"""Independent distance, projection, directrix and example checks for C049."""
from pathlib import Path
import math
import json
import re

ROOT=Path(__file__).resolve().parents[3]
UID=Path(__file__).resolve().parents[1]
def close(a,b):
    assert math.isclose(a,b,rel_tol=2e-10,abs_tol=2e-10),(a,b)
def distances(a,b,p):
    c=math.sqrt(a*a-b*b);e=c/a;x,y=p
    close(x*x/(a*a)+y*y/(b*b),1)
    r1=math.hypot(x+c,y);r2=math.hypot(x-c,y)
    close(r1,a+e*x);close(r2,a-e*x)
    close(r1+r2,2*a);close(r1-r2,2*e*x)
    close(r1*r1-r2*r2,4*c*x)
    close(r1*r2,a*a-e*e*x*x)
    assert a-c-1e-10<=r1<=a+c+1e-10
    assert b*b-1e-10<=r1*r2<=a*a+1e-10
    d=a*a/c
    assert d>a and -d<x<d
    close(r1,e*(x+d));close(r2,e*(d-x))
    close(math.hypot(abs(x+c),abs(y)),r1)
    close(math.hypot(abs(x-c),abs(y)),r2)
    # Rotate 90 degrees: old left/right foci become lower/upper foci.
    xp,yp=-y,x
    close(math.hypot(xp,yp+c),a+e*yp)
    close(math.hypot(xp,yp-c),a-e*yp)
    return r1,r2

states=0
for a,b in [(5,4),(5,3),(2,1),(3,2.9),(7,.7)]:
    for n in range(121):
        t=2*math.pi*n/120
        distances(a,b,(a*math.cos(t),b*math.sin(t)));states+=1

for p,expected in [((3,16/5),(34/5,16/5)),((-5,0),(2,8)),((0,4),(5,5)),((5,0),(8,2)),
                   ((2,4*math.sqrt(21)/5),(31/5,19/5)),((4,2.4),(37/5,13/5)),
                   ((5/3,8*math.sqrt(2)/3),(6,4))]:
    for actual,target in zip(distances(5,4,p),expected):close(actual,target)
close(distances(5,3,(2.5,3*math.sqrt(3)/2))[0],7)
close(distances(5,3,(2.5,3*math.sqrt(3)/2))[1],3)
# All examples' extrema and equalities.
close(distances(5,4,(0,4))[0]*distances(5,4,(0,4))[1],25)
close(distances(5,4,(5,0))[0]*distances(5,4,(5,0))[1],16)
# Actual TikZ inputs: do not let geometry silently drift from audited points.
for suffix in ['focal_radius_main','directrix_distances','focus_axis_comparison']:
    source=(ROOT/'assets/tikz'/f'C049_{suffix}.tex').read_text(encoding='utf-8')
    assert r'\coordinate (P) at (3,3.2);' in source
assert r'\coordinate (P) at (-3.2,3);' in (ROOT/'assets/tikz/C049_focus_axis_comparison.tex').read_text(encoding='utf-8')
source=(ROOT/'assets/tikz/C049_focal_radius_three_states.tex').read_text(encoding='utf-8')
for p in ['(-5,0)','(0,4)','(5,0)']:assert r'\coordinate (P) at '+p+';' in source
source=(ROOT/'assets/tikz/C049_pythagoras_foot_positions.tex').read_text(encoding='utf-8')
for p in ['(2,{4*sqrt(21)/5})','(4,2.4)']:assert r'\coordinate (P) at '+p+';' in source
for p in UID.glob('0[1-6]_*.tex'):
    for name in re.findall(r'\\input\{([^}]+)\}',p.read_text(encoding='utf-8')):
        assert (ROOT/(name+'.tex')).is_file(),name
meta=json.loads((UID/'meta.json').read_text(encoding='utf-8'))
assert meta['interactive']['has_diagram'] is True
assert meta['id']=='C049'
print(f'C049 PASS: {states} independent full-ellipse states, both half-planes, endpoints, directrices, rotation, Pythagoras, all actual figure points, 5 examples and TeX references.')
