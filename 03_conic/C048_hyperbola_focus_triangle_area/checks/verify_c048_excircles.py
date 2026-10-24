"""Independent Euclidean checks for method five, on both hyperbola branches."""
import math
from pathlib import Path
import re

def sub(p,q): return tuple(a-b for a,b in zip(p,q))
def dot(p,q): return sum(a*b for a,b in zip(p,q))
def dist(p,q): return math.hypot(*sub(p,q))
def area(a,b,c):
    u,v=sub(b,a),sub(c,a)
    return abs(u[0]*v[1]-u[1]*v[0])/2
def close(a,b): assert math.isclose(a,b,rel_tol=2e-8,abs_tol=2e-8),(a,b)
def foot(i,a,b):
    v=sub(b,a); t=dot(sub(i,a),v)/dot(v,v)
    return tuple(a[k]+t*v[k] for k in range(2)),t

def check(a,b,p):
    c=math.hypot(a,b)
    f1,f2=(-c,0),(c,0)
    if dist(p,f1)<dist(p,f2): f1,f2=f2,f1
    vertices=[f1,p,f2]
    m,n=dist(p,f1),dist(p,f2)
    sides=[n,2*c,m]; s=sum(sides)/2; S=area(*vertices)
    close(m-n,2*a)
    centers=[]; radii=[]; allfeet=[]
    for j in range(3):
        weights=[(-v if k==j else v) for k,v in enumerate(sides)]
        i=tuple(sum(weights[k]*vertices[k][d] for k in range(3))/sum(weights) for d in range(2))
        r=S/(s-sides[j]); centers.append(i); radii.append(r)
        feet=[]
        for k in range(3):
            u,v=vertices[(k+1)%3],vertices[(k+2)%3]
            t,ratio=foot(i,u,v); feet.append(t)
            close(dist(i,t),r); close(dot(sub(i,t),sub(v,u)),0)
            assert (0<ratio<1) if j==k else (ratio<0 or ratio>1)
        # The two contact segments from each vertex have equal lengths.
        for k in range(3):
            others=[v for z,v in enumerate(feet) if z!=k]
            close(dist(vertices[k],others[0]),dist(vertices[k],others[1]))
        # Each excenter is on the named vertex's interior angle bisector.
        u,v=sub(vertices[(j+1)%3],vertices[j]),sub(vertices[(j+2)%3],vertices[j])
        w=sub(i,vertices[j])
        close(dot(w,u)/math.hypot(*u),dot(w,v)/math.hypot(*v))
        allfeet.append(feet)
    i=centers[0]; r=radii[0]; t=allfeet[0][0]
    close(dist(p,t),c-a)
    u,v=sub(f1,p),sub(f2,p)
    theta=math.acos(max(-1,min(1,dot(u,v)/(m*n))))
    close(r,(c-a)/math.tan(theta/2))
    close(S,(a+c)*r)
    close(S,area(i,f1,p)+area(i,f1,f2)-area(i,p,f2))
    close(S,b*b/math.tan(theta/2))
    close(S,(s-2*c)*radii[1]);close(S,(c-a)*radii[2])
    return centers,radii,allfeet

states=0
for a,b in [(1,math.sqrt(3)),(2,1),(1,4),(3,4),(4,.75)]:
    for u in [.12,.3,.65,1,1.5,2]:
        for sx in [-1,1]:
            for sy in [-1,1]:
                check(a,b,(sx*a*math.cosh(u),sy*b*math.sinh(u)));states+=1

# Match the actual coordinates written to the three TikZ sources.
centers,radii,feet=check(1,math.sqrt(3),(2.5,1.5*math.sqrt(7)))
root=Path(__file__).resolve().parents[3]
for j,suffix in enumerate(['f1','p','f2']):
    text=(root/'assets/tikz'/f'C048_excircle_opposite_{suffix}.tex').read_text(encoding='utf-8')
    coords={n:(float(x),float(y)) for n,x,y in re.findall(r'\\coordinate \((\w+)\) at \(([-\d.]+),([-\d.]+)\)',text)}
    for v,w in zip(coords['I'],centers[j]):close(v,w)
    circle=float(re.search(r'circle \(([\d.]+)\)',text)[1]);close(circle,radii[j])
    for f in 'TUV':
        close(min(dist(coords[f],v) for v in feet[j]),0)
print(f'C048 excircles PASS: {states} states on both branches and both half-planes; all three actual TikZ circles, tangencies, bisectors, equal tangents, exterior half-angle and signed-area formula.')
