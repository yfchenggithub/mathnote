import math,json
from pathlib import Path
count=0
for a,b in [(2,math.sqrt(3)),(5,3),(3,2.9),(4,1)]:
    c=math.sqrt(a*a-b*b)
    for degree in range(181):
        q=math.radians(degree);u,v=math.cos(q),math.sin(q)
        for sign in [-1,1]:
            alpha=u*u/(a*a)+v*v/(b*b)
            beta=2*sign*c*u/(a*a); gamma=-b*b/(a*a)
            delta=beta*beta-4*alpha*gamma
            assert math.isclose(delta,4/(a*a),rel_tol=1e-10)
            t1=(-beta+math.sqrt(delta))/(2*alpha)
            t2=(-beta-math.sqrt(delta))/(2*alpha)
            assert t1>0>t2
            r=b*b/(a+sign*c*u);s=b*b/(a-sign*c*u)
            assert math.isclose(r,t1,rel_tol=1e-10)
            assert math.isclose(s,-t2,rel_tol=1e-10)
            A=(sign*c+r*u,r*v);B=(sign*c-s*u,-s*v)
            for point in [A,B]:
                x,y=point
                assert math.isclose(x*x/(a*a)+y*y/(b*b),1,abs_tol=1e-10)
                assert math.isclose(math.dist(point,(-c,0))+math.dist(point,(c,0)),2*a,rel_tol=1e-10)
            L=2*a*b*b/(a*a-c*c*u*u)
            assert math.isclose(math.dist(A,B),L,rel_tol=1e-10)
            assert 2*b*b/a-1e-9<=L<=2*a+1e-9
            assert math.isclose(L,r+s,rel_tol=1e-10)
            count+=1
# Representative illustrations and all eight example results.
assert math.isclose(12/(4-.25),16/5)
assert math.isclose(12/(4-math.cos(math.radians(120))**2),16/5)
assert math.isclose((8/5)*2,16/5)
assert math.isclose(90/(25-16/2),90/17)
assert math.isclose(2*9/5,18/5)
assert 18/5<10
assert 3<2*math.sqrt(3)
a,b,c=5,3,4;q=math.radians(30);u,v=math.cos(q),math.sin(q)
alpha=u*u/(b*b)+v*v/(a*a);beta=2*c*v/(a*a);gamma=-b*b/(a*a)
delta=beta*beta-4*alpha*gamma
t1=(-beta+math.sqrt(delta))/(2*alpha);t2=(-beta-math.sqrt(delta))/(2*alpha)
assert math.isclose(t1-t2,30/7,rel_tol=1e-10)
for t in [t1,t2]:
    x,y=t*u,c+t*v
    assert math.isclose(x*x/9+y*y/25,1,abs_tol=1e-10)
assert math.isclose(9/(5+4*v),t1) and math.isclose(9/(5-4*v),-t2)
# Added notation figure: independently verify both endpoints and signed projections.
a,b,c=3,math.sqrt(5),2
r,s=1.25,2.5
u,v=.5,math.sqrt(3)/2
A=(c+r*u,r*v);B=(c-s*u,-s*v)
for X in (A,B):
    assert math.isclose(X[0]**2/a**2+X[1]**2/b**2,1,abs_tol=1e-12)
assert math.isclose(math.dist(A,(c,0)),r)
assert math.isclose(math.dist(B,(c,0)),s)
assert math.isclose(math.dist(A,B),r+s)
assert math.isclose(A[1],1.08253175,abs_tol=1e-8)
assert math.isclose(B[1],-2.16506351,abs_tol=1e-8)
names=['definition_pythagoras_b','proof_notation','focal_chord_split','three_directions','definition_pythagoras','left_right_focus','supplementary_angles','ordinary_chord_vs_latus','vertical_major_axis_angle']
for name in names:
    txt=Path('assets/tikz/C052_'+name+'.tex').read_text(encoding='utf-8')
    assert '\\tiny' not in txt and '\\scriptsize' not in txt
meta=json.loads(Path('03_conic/C052_ellipse_focal_chord_length/meta.json').read_text(encoding='utf-8'))
assert meta['id']=='C052' and meta['interactive']['has_diagram']
result={'uid':'C052','independent_quadratic_states':count,'ellipse_parameter_sets':4,'examples_checked':8,'tikz_diagrams':9,'rotated_axis_model':'PASS','result':'PASS'}
Path('.tmp/C052_tikz_review/math_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
