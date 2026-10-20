"""C016: branch-aware hyperbolic parametrisation and Euclidean triangle centres."""
import math


def dot(u,v): return sum(x*y for x,y in zip(u,v))
def add(u,v): return tuple(x+y for x,y in zip(u,v))
def sub(u,v): return tuple(x-y for x,y in zip(u,v))
def mul(k,u): return tuple(k*x for x in u)
def norm(u): return math.hypot(*u)


def projection(x,a,b):
    v=sub(b,a)
    return add(a,mul(dot(sub(x,a),v)/dot(v,v),v))


def state(u,branch=1,a=3.,b=4.):
    if a<=0 or b<=0 or branch not in (-1,1): raise ValueError('Positive axes and branch +/-1 required')
    if abs(u)<1e-10: raise ValueError('Exclude the degenerate vertices')
    c=math.hypot(a,b); e=c/a
    p=(branch*a*math.cosh(u),b*math.sinh(u)); x,y=p
    f1,f2=(-c,0.),(c,0.)
    r1,r2=norm(sub(p,f1)),norm(sub(p,f2))
    perimeter=2*c+r1+r2
    g=mul(1/3,add(add(p,f1),f2))
    inc=mul(1/perimeter,add(add(mul(2*c,p),mul(r2,f1)),mul(r1,f2)))
    radius=2*c*abs(y)/perimeter
    h=(x,(c*c-x*x)/y)
    circum=(0.,(x*x+y*y-c*c)/(2*y))
    return dict(a=a,b=b,c=c,e=e,u=u,branch=branch,p=p,f1=f1,f2=f2,r1=r1,r2=r2,
                g=g,i=inc,h=h,circum=circum,radius=radius,circumradius=norm(sub(circum,f1)),
                t=projection(inc,f1,f2),contact1=projection(inc,f1,p),contact2=projection(inc,f2,p),
                altfoot=projection(f1,f2,p),verticalfoot=(x,0.),
                mid1=mul(.5,add(p,f2)),mid2=mul(.5,add(p,f1)))


def from_incentre(t,branch=1,a=3.,b=4.):
    if not 0<abs(t)<b or branch not in (-1,1) or a<=0: raise ValueError('Require 0<|t|<b')
    return branch*a*(b*b+t*t)/(b*b-t*t),2*b*b*t/(b*b-t*t)


def clip_line(A,B,C,box=(-6.4,6.4,-4.6,6.6)):
    xmin,xmax,ymin,ymax=box; points=[]
    if abs(B)>1e-12:
        for x in (xmin,xmax):
            y=(C-A*x)/B
            if ymin-1e-9<=y<=ymax+1e-9: points.append((x,y))
    if abs(A)>1e-12:
        for y in (ymin,ymax):
            x=(C-B*y)/A
            if xmin-1e-9<=x<=xmax+1e-9 and not any(math.hypot(x-u,y-v)<1e-8 for u,v in points): points.append((x,y))
    if len(points)!=2: raise ValueError('Expected two visible line intersections')
    return points
