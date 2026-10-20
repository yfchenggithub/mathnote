"""C015 triangle centres and true Euclidean constructions; renderer independent."""
import math


def add(u,v): return tuple(x+y for x,y in zip(u,v))
def sub(u,v): return tuple(x-y for x,y in zip(u,v))
def mul(k,u): return tuple(k*x for x in u)
def dot(u,v): return sum(x*y for x,y in zip(u,v))
def norm(u): return math.hypot(*u)


def project(x,a,b):
    direction=sub(b,a)
    return add(a,mul(dot(sub(x,a),direction)/dot(direction,direction),direction))


def state(theta,a=5.,b=4.):
    if not a>b>0: raise ValueError('Require a>b>0')
    c=math.sqrt(a*a-b*b)
    p=(a*math.cos(theta),b*math.sin(theta))
    x,y=p
    if abs(y)<1e-10: raise ValueError('Nondegenerate triangle requires y0 != 0')
    f1,f2=(-c,0.),(c,0.)
    r1,r2=norm(sub(p,f1)),norm(sub(p,f2))
    g=mul(1/3,add(add(p,f1),f2))
    perimeter=2*c+r1+r2
    inc=mul(1/perimeter,add(add(mul(2*c,p),mul(r2,f1)),mul(r1,f2)))
    area=c*abs(y)
    radius=2*area/perimeter
    h=(x,(c*c-x*x)/y)
    circum=(0.,(x*x+y*y-c*c)/(2*y))
    circumradius=norm(sub(circum,f1))
    return dict(a=a,b=b,c=c,e=c/a,p=p,f1=f1,f2=f2,r1=r1,r2=r2,g=g,i=inc,h=h,
                circum=circum,circumradius=circumradius,radius=radius,area=area,
                t=(inc[0],0.),u=project(inc,f1,p),v=project(inc,f2,p),
                altfoot=project(f1,f2,p),verticalfoot=(x,0.),
                midpoint1=mul(.5,add(p,f2)),midpoint2=mul(.5,add(p,f1)))


def clip_line(A,B,C,box=(-5.6,5.6,-4.8,4.8)):
    xmin,xmax,ymin,ymax=box; hits=[]
    if abs(B)>1e-12:
        for x in (xmin,xmax):
            y=(C-A*x)/B
            if ymin-1e-9<=y<=ymax+1e-9: hits.append((x,y))
    if abs(A)>1e-12:
        for y in (ymin,ymax):
            x=(C-B*y)/A
            if xmin-1e-9<=x<=xmax+1e-9 and not any(math.hypot(x-u,y-v)<1e-8 for u,v in hits): hits.append((x,y))
    if len(hits)!=2: raise ValueError('Expected two rectangle intersections')
    return hits
