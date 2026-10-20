"""C013: tangent from endpoint-intercept ratio, Euclidean coordinates."""
import math


def state(u, a=2.0, b=1.0, side=1):
    if not a>b>0 or side not in (-1,1):
        raise ValueError('Require a>b>0 and side=+1 or -1')
    yl,yr=side*b*math.exp(u),side*b*math.exp(-u)
    k=(yr-yl)/(2*a)
    m=(yl+yr)/2
    p=(-a*a*k/m,b*b/m)
    return dict(p=p,p1=(-a,yl),p2=(a,yr),a1=(-a,0),a2=(a,0),
                d1=abs(yl),d2=abs(yr),k=k,m=m,area=a*(abs(yl)+abs(yr)))


def shoelace(vertices):
    return abs(sum(x*v-y*u for (x,y),(u,v) in zip(vertices,vertices[1:]+vertices[:1])))/2
