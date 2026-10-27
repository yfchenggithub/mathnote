"""C084 independent mathematical model; no renderer dependencies."""
from dataclasses import dataclass
from math import cosh, sinh, hypot, atan2, pi

@dataclass(frozen=True)
class FocalState:
    a: float
    b: float
    x: float
    y: float

    def __post_init__(self):
        if self.a <= 0 or self.b <= 0 or self.y == 0:
            raise ValueError('Positive semiaxes and a nonvertex point are required')
        if abs(self.x**2/self.a**2-self.y**2/self.b**2-1)>1e-7:
            raise ValueError('P must lie on this hyperbola')

    @property
    def c(self): return hypot(self.a,self.b)
    @property
    def p(self): return (self.x,self.y)
    @property
    def f1(self): return (-self.c,0.)
    @property
    def f2(self): return (self.c,0.)
    @property
    def m(self): return self.a*self.a/self.x
    @property
    def n(self): return self.c*self.c*self.x/(self.a*self.a)
    @property
    def r1(self): return hypot(self.x+self.c,self.y)
    @property
    def r2(self): return hypot(self.x-self.c,self.y)
    @property
    def tangent(self): return (self.a**2*self.y,self.b**2*self.x)
    @property
    def normal(self): return (self.b**2*self.x,-self.a**2*self.y)
    @property
    def units(self):
        return ((-self.c-self.x)/self.r1,-self.y/self.r1),((self.c-self.x)/self.r2,-self.y/self.r2)

def state(t,a=3.,b=4.,branch=1,upper=1):
    if t<=0 or branch not in (-1,1) or upper not in (-1,1):
        raise ValueError('t>0 and signs +/-1 are required')
    return FocalState(a,b,branch*a*cosh(t),upper*b*sinh(t))

def direction(p,q): return atan2(q[1]-p[1],q[0]-p[0])
def sweep(start,end): return (end-start+pi)%(2*pi)-pi

def clip_line(p,d,bounds):
    """Analytic intersection of an infinite line with a Cartesian rectangle."""
    xmin,xmax,ymin,ymax=bounds; hits=[]
    if abs(d[0])>1e-12:
        for x in (xmin,xmax):
            y=p[1]+(x-p[0])*d[1]/d[0]
            if ymin-1e-9<=y<=ymax+1e-9:hits.append((x,y))
    if abs(d[1])>1e-12:
        for y in (ymin,ymax):
            x=p[0]+(y-p[1])*d[0]/d[1]
            if xmin-1e-9<=x<=xmax+1e-9:hits.append((x,y))
    unique=[]
    for q in hits:
        if not any(hypot(q[0]-v[0],q[1]-v[1])<1e-8 for v in unique):unique.append(q)
    if len(unique)!=2:raise ValueError((p,d,bounds,unique))
    return unique
