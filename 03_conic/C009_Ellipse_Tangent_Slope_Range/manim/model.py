"""C009 independent slope-set and point-constrained tangent model."""
from dataclasses import dataclass
from math import isclose,isfinite,sqrt


@dataclass(frozen=True)
class SlopeRangeModel:
    a: float=2.
    b: float=1.

    def __post_init__(self):
        if not(all(isfinite(v) for v in (self.a,self.b)) and self.a>self.b>0):
            raise ValueError('Require finite a>b>0')

    def parallel_pair(self,k):
        if not isfinite(k):
            raise ValueError('A vertical direction has no real slope')
        R=sqrt(self.a*self.a*k*k+self.b*self.b)
        return [((-k,1.,m),(-self.a*self.a*k/m,self.b*self.b/m)) for m in (R,-R)]

    def position(self,p):
        return (p[0]/self.a)**2+(p[1]/self.b)**2

    def point_tangents(self,p):
        """General-form lines (A,B,C) mean Ax+By=C; vertical lines need no slope."""
        u,v=p[0]/self.a,p[1]/self.b; S=u*u+v*v
        if isclose(S,1,rel_tol=1e-12,abs_tol=1e-12):
            points=[p]
        elif S<1:
            points=[]
        else:
            f=sqrt(S-1)/S
            points=[(self.a*(u/S-s*v*f),self.b*(v/S+s*u*f)) for s in (-1,1)]
        return [((x/self.a**2,y/self.b**2,1.),(x,y)) for x,y in points]

    def slope_equation(self,p):
        x,y=p
        return self.a*self.a-x*x,2*x*y,self.b*self.b-y*y

    def finite_roots(self,p):
        A,B,C=self.slope_equation(p)
        if abs(A)<1e-12:
            return [] if abs(B)<1e-12 else [-C/B]
        D=B*B-4*A*C
        if D < -1e-11:
            return []
        if abs(D)<1e-11:
            return [-B/(2*A)]
        return sorted([(-B-sqrt(D))/(2*A),(-B+sqrt(D))/(2*A)])


def clip_line(A,B,C,xmax=2.75,ymax=2.25):
    points=[]
    if A==0 and B==0:
        raise ValueError('Invalid line')
    if B!=0:
        for x in (-xmax,xmax):
            y=(C-A*x)/B
            if abs(y)<=ymax+1e-10:
                points.append((x,y))
    if A!=0:
        for y in (-ymax,ymax):
            x=(C-B*y)/A
            if abs(x)<=xmax+1e-10 and all(abs(x-u)+abs(y-v)>1e-9 for u,v in points):
                points.append((x,y))
    return points[:2]
