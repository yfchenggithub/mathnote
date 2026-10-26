from pathlib import Path
import math,json

count=0
def near(a,b):assert math.isclose(a,b,rel_tol=2e-9,abs_tol=2e-9),(a,b)
# Independent roots of the intersected line and parabola, four openings.
for p in [.5,2,5]:
 for axis in ['x','y']:
  for sign in [-1,1]:
   for deg in range(180):
    if axis=='x' and deg==0 or axis=='y' and deg==90:continue
    q=math.radians(deg);u,v=math.cos(q),math.sin(q)
    m=sign*(u if axis=='x' else v)
    alpha=v*v if axis=='x' else u*u
    beta=-2*p*m;gamma=-p*p
    delta=beta*beta-4*alpha*gamma
    z=-.5*(beta+math.copysign(math.sqrt(delta),beta))
    t1,t2=sorted([z/alpha,gamma/z],reverse=True)
    assert t1>0>t2
    near(t1,p/(1-m));near(-t2,p/(1+m))
    F=(sign*p/2,0) if axis=='x' else (0,sign*p/2)
    points=[]
    for t in [t1,t2]:
     x,y=F[0]+t*u,F[1]+t*v
     near(y*y,sign*2*p*x) if axis=='x' else near(x*x,sign*2*p*y)
     d=abs(x+sign*p/2) if axis=='x' else abs(y+sign*p/2)
     near(math.dist((x,y),F),d)
     points.append((x,y))
    near(math.dist(*points),2*p/alpha)
    assert t1-t2>=2*p-1e-9
    if axis=='x':
     near(points[0][1]+points[1][1],2*p*v*m/alpha)
    count+=1
# All six numbered examples and the ratio extension.
near(4/math.sin(math.pi/6)**2,16)
for d in [45,135]:near(8/math.sin(math.radians(d))**2,16)
near(2*3/math.sin(math.pi/3)**2,8)
near(6/math.sin(2*math.pi/3)**2,8)
near(8*(1+2**2)/2**2,10);near(2*4,8)
A=(3,2*math.sqrt(3));B=(1/3,-2*math.sqrt(3)/3);F=(1,0)
near(A[1]**2,4*A[0]);near(B[1]**2,4*B[0])
near(math.dist(A,F),4);near(math.dist(B,F),4/3);near(math.dist(A,B),16/3)
for deg in [30,150]:
 c=math.cos(math.radians(deg));r=2/(1-c);s=2/(1+c)
 near((r+s)/4,4);near(r/s,(1+c)/(1-c))
near((2+math.sqrt(3))/(2-math.sqrt(3)),(1+math.sqrt(3)/2)/(1-math.sqrt(3)/2))
# Projections in both proof figures and the rotated illustration.
near(4,2+4*.5);near(4/3,2-(4/3)*.5)
for x,y in [(2*math.sqrt(3),3),(-2*math.sqrt(3)/3,1/3)]:near(x*x,4*y)
near(math.dist((2*math.sqrt(3),3),(-2*math.sqrt(3)/3,1/3)),16/3)
near(4/math.cos(math.pi/6)**2,16/3)
names=['focal_chord_notation','forward_projection','backward_projection','angle_comparison','opening_reflection','validity_comparison','vertical_axis_angle']
for n in names:
 s=Path('assets/tikz/C053_'+n+'.tex').read_text(encoding='utf-8')
 assert '\\tiny' not in s and '\\scriptsize' not in s and '\t' not in s
m=json.loads(Path('03_conic/C053_parabola_focal_chord_length_inclination/meta.json').read_text(encoding='utf-8'))
assert m['id']=='C053' and m['interactive']['has_diagram']
result={'uid':'C053','independent_intersection_states':count,'openings':4,'parameter_sets':3,'numbered_examples':6,'ratio_extension':'PASS','two_projection_models':'PASS','rotated_axis_model':'PASS','new_tikz_diagrams':7,'result':'PASS'}
Path('.tmp/C053_tikz_review/math_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
