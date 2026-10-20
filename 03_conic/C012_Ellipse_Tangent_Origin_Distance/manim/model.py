"""C012 Euclidean geometry; no renderer dependencies."""
import math


def state(t, a=3.0, b=2.0):
    if not a > b > 0:
        raise ValueError('Require a > b > 0')
    x, y = a*math.cos(t), b*math.sin(t)
    c = math.sqrt(a*a-b*b)
    A, B = x/a**2, y/b**2
    norm2 = A*A+B*B
    h = (A/norm2, B/norm2)
    r1, r2 = math.hypot(x+c,y), math.hypot(x-c,y)
    return dict(p=(x,y), f1=(-c,0), f2=(c,0), line=(A,B,1), h=h,
                r1=r1, r2=r2, g=math.sqrt(r1*r2), d=1/math.sqrt(norm2))


def clip_line(A, B, C, box=(-3.55,3.55,-3.0,3.0)):
    xmin,xmax,ymin,ymax=box
    hits=[]
    if abs(B)>1e-12:
        for x in (xmin,xmax):
            y=(C-A*x)/B
            if ymin-1e-9<=y<=ymax+1e-9:
                hits.append((x,y))
    if abs(A)>1e-12:
        for y in (ymin,ymax):
            x=(C-B*y)/A
            if xmin-1e-9<=x<=xmax+1e-9 and not any(math.hypot(x-u,y-v)<1e-8 for u,v in hits):
                hits.append((x,y))
    if len(hits)!=2:
        raise ValueError('Expected two rectangle intersections')
    return hits
