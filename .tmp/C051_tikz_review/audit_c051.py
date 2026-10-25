import math,json
from pathlib import Path
states=0
for p in [1,2,3,6]:
    for i in range(-30,31):
        u=i/5
        t=u*u/(2*p)
        for a in [0,math.pi/2,math.pi,3*math.pi/2]:
            def rot(x,y): return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a))
            P=rot(t,u); F=rot(p/2,0); Q=rot(-p/2,u)
            assert math.isclose(math.dist(P,F),t+p/2,abs_tol=1e-10)
            assert math.isclose(math.dist(P,Q),math.dist(P,F),abs_tol=1e-10)
            directrix_direction=rot(0,1)
            assert abs(sum((P[j]-Q[j])*directrix_direction[j] for j in (0,1)))<1e-10
            assert math.dist(P,F)>=p/2-1e-10
            if i==0: assert math.isclose(math.dist(P,F),p/2)
            states+=1
    A=(p/2,p);B=(p/2,-p)
    assert math.isclose(math.dist(A,B),2*p)
    assert math.isclose(math.dist(A,(p/2,0)),p)
    assert math.isclose(A[1]**2,2*p*A[0])
assert math.isclose(math.dist((3,math.sqrt(12)),(1,0)),4)
assert math.isclose(math.dist((4,math.sqrt(32)),(2,0)),6)
assert math.dist((4,4),(1,0))==5
assert abs(1*4)/2==2
assert math.isclose(math.dist((-3,math.sqrt(24)),(-2,0)),5)
assert math.isclose(math.dist((math.sqrt(30),5),(0,1.5)),6.5)
assert math.isclose(math.dist((math.sqrt(30),-5),(0,-1.5)),6.5)
assert math.dist((0,0),(3,0))==3
assert math.dist((3,0),(1,0))==2 and math.dist((3,0),(-1,0))==4
root=Path('03_conic/C051_parabola_focal_radius_coordinate')
meta=json.loads((root/'meta.json').read_text(encoding='utf-8'))
assert meta['id']=='C051' and meta['interactive']['has_diagram']
names=['focus_directrix_split','math_audit_geometry','four_openings','area_height','on_curve_requirement']
for n in names:
    s=Path('assets/tikz/C051_'+n+'.tex').read_text(encoding='utf-8')
    assert '\\tiny' not in s and '\\scriptsize' not in s
print(json.dumps({'uid':'C051','four_direction_states':states,'latus_rectum_parameters':4,'examples':7,'tikz_files':5,'result':'PASS'},indent=2))
