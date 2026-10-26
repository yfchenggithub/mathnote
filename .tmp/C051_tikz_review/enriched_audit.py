from pathlib import Path
import math,json,runpy
runpy.run_path('.tmp/C051_tikz_review/audit_c051.py')
triangles=0
for p in [1,2,3,6]:
    for i in range(-30,31):
        y=i/5; x=y*y/(2*p)
        horizontal=abs(x-p/2)
        assert math.isclose(math.hypot(horizontal,y),x+p/2,abs_tol=1e-10)
        assert math.isclose((x-p/2)**2+y*y,(x+p/2)**2,abs_tol=1e-10)
        triangles+=1
inverse_cases=0
for p in [1,2,3,6]:
    for factor in [0,.25,.5,1,2,5]:
        r=p*factor; x=r-p/2
        if r<p/2:
            assert 2*p*x<0
        elif r==p/2:
            assert x==0 and math.dist((0,0),(p/2,0))==r
        else:
            y=math.sqrt(2*p*x)
            assert y>0
            for sign in [-1,1]:
                assert math.isclose(math.dist((x,sign*y),(p/2,0)),r)
        inverse_cases+=1
for x,y,r in [(0,0,1),(1,2,2),(4,4,5)]:
    assert y*y==4*x and math.dist((x,y),(1,0))==r
assert math.isclose(math.dist((4,4*math.sqrt(2)),(2,0)),6)
assert math.isclose(math.dist((4,-4*math.sqrt(2)),(2,0)),6)
for name in ['position_and_minimum','coordinate_right_triangle','inverse_two_points']:
    text=Path('assets/tikz/C051_'+name+'.tex').read_text(encoding='utf-8')
    assert '\\tiny' not in text and '\\scriptsize' not in text
print(json.dumps({'coordinate_triangle_states':triangles,'inverse_boundary_cases':inverse_cases,'new_figures':3,'total_figures':8,'result':'PASS'},indent=2))
