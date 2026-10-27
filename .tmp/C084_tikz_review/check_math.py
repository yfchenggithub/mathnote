import math,json
from pathlib import Path
checks=0
def eq(a,b,tol=1e-8):
 global checks
 assert math.isclose(a,b,rel_tol=tol,abs_tol=tol),(a,b)
 checks+=1
for a,b in [(3,4),(1,1),(2,math.sqrt(3)),(5,2)]:
 c=math.hypot(a,b)
 for sign in [-1,1]:
  for side in [-1,1]:
   for t in [.001,.15,.7,1.4,3]:
    x=sign*a*math.cosh(t);y=side*b*math.sinh(t)
    r1=math.hypot(x+c,y);r2=math.hypot(x-c,y)
    m=c*(r1-r2)/(r1+r2)
    eq(x*m,a*a);eq(abs(r1-r2),2*a);eq(r1*r1-r2*r2,4*c*x)
    eq((c+m)/(c-m),r1/r2)
    assert 0<abs(m)<a and m*x>0
    eq(r1,(c/a)*abs(x)+sign*a);eq(r2,(c/a)*abs(x)-sign*a)
    # Incenter from side-weighted Cartesian vertices, independently computed.
    ix=(2*c*x-c*r2+c*r1)/(2*c+r1+r2)
    iy=2*c*y/(2*c+r1+r2)
    eq(ix,sign*a);eq((ix-m)*y,(x-m)*iy)
    # Tangent gradient is collinear with the normal perpendicular to PM.
    eq((x/a**2)*(m-x)+(-y/b**2)*(-y),0)
    u1=((-c-x)/r1,-y/r1);u2=((c-x)/r2,-y/r2)
    v=(u1[0]+u2[0],u1[1]+u2[1])
    eq(v[0]*(-y)-v[1]*(m-x),0)
eq(math.hypot(8.75,3),37/4);eq(math.hypot(-1.25,3),13/4)
eq(20*3.75-9*3,48);eq(-20*(-3.75)-9*3,48)
eq(6**2/9-(4*math.sqrt(3))**2/16,1);eq(9/6,1.5)
# Exact incircle data and perpendicular projections used in the diagram.
I=(3,4/3);P=(15/4,3);L=(-5,0);R=(5,0)
for A,Q in [(L,(2.567568,2.594595)),(R,(4.230769,1.846154))]:
 d=(P[0]-A[0],P[1]-A[1]);q=((I[0]-A[0])*d[0]+(I[1]-A[1])*d[1])/(d[0]**2+d[1]**2)
 exact=(A[0]+q*d[0],A[1]+q*d[1]);eq(exact[0],Q[0],1e-6);eq(exact[1],Q[1],1e-6)
 eq(math.dist(I,exact),4/3)
print(json.dumps({'status':'PASS','numeric_equalities':checks,'nondegenerate_cases':80,'conditions':'a,b>0; both branches; both signs of y; near-vertex to distant points','boundary':'vertices excluded: collinear focal triangle'},ensure_ascii=False,indent=2))
