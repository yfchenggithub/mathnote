"""Five C014 properties from one UID-local Euclidean support-line model."""
import math


def dot(u,v): return sum(x*y for x,y in zip(u,v))
def add(u,v): return tuple(x+y for x,y in zip(u,v))
def sub(u,v): return tuple(x-y for x,y in zip(u,v))
def mul(k,u): return tuple(k*x for x in u)
def length(u): return math.hypot(*u)
def unit(u): return mul(1/length(u),u)


def state(phi,a=3.0,b=2.0):
    if not a>b>0: raise ValueError('Require a>b>0')
    c=math.sqrt(a*a-b*b)
    n=(math.cos(phi),math.sin(phi))
    h=math.sqrt(a*a*n[0]**2+b*b*n[1]**2)
    p=(a*a*n[0]/h,b*b*n[1]/h)
    f1,f2=(-c,0.),(c,0.)
    d1,d2=h-dot(n,f1),h-dot(n,f2)
    h1,h2=add(f1,mul(d1,n)),add(f2,mul(d2,n))
    q=sub(mul(2,h1),f1)
    r1,r2=length(sub(p,f1)),length(sub(p,f2))
    incoming=unit(sub(p,f1))
    reflected=sub(incoming,mul(2*dot(incoming,n),n))
    xm=None if abs(p[1])<1e-10 else c*c*p[0]/(a*a)
    xn=None if abs(p[0])<1e-10 else a*a/p[0]
    chord=length(sub(h2,h1))
    vertices=[f1,h1,h2,f2]
    area=abs(sum(x*v-y*u for (x,y),(u,v) in zip(vertices,vertices[1:]+vertices[:1])))/2
    return dict(a=a,b=b,c=c,n=n,h=h,p=p,f1=f1,f2=f2,h1=h1,h2=h2,
                d1=d1,d2=d2,q=q,r1=r1,r2=r2,reflected=reflected,
                xm=xm,xn=xn,chord=chord,area=area)


def area_maximum(a,b):
    c=math.sqrt(a*a-b*b)
    t=min(1.,a*a/(2*c*c))
    return (2*b*c if c<=b else a*a), math.asin(math.sqrt(t))


def clip_line(n,h,box=(-3.5,3.5,-3.0,3.0)):
    A,B=n; xmin,xmax,ymin,ymax=box; hits=[]
    if abs(B)>1e-12:
        for x in (xmin,xmax):
            y=(h-A*x)/B
            if ymin-1e-9<=y<=ymax+1e-9: hits.append((x,y))
    if abs(A)>1e-12:
        for y in (ymin,ymax):
            x=(h-B*y)/A
            if xmin-1e-9<=x<=xmax+1e-9 and not any(math.hypot(x-u,y-v)<1e-8 for u,v in hits): hits.append((x,y))
    if len(hits)!=2: raise ValueError('Expected two line/rectangle intersections')
    return hits


def beam(phi,progress,a=3.,b=2.):
    s=state(phi,a,b)
    distance=max(0,min(1,progress))*(s['r1']+s['r2'])
    if distance<=s['r1']:
        return add(s['f1'],mul(distance/s['r1'],sub(s['p'],s['f1'])))
    return add(s['p'],mul((distance-s['r1'])/s['r2'],sub(s['f2'],s['p'])))
