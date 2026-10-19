"""C007 independent line/ellipse intersection and tangency geometry."""
from dataclasses import dataclass
from math import isclose, isfinite, sqrt


@dataclass(frozen=True)
class SlopeTangentModel:
    a: float = 3.0
    b: float = 2.0
    k: float = .5

    def __post_init__(self):
        if not (all(isfinite(v) for v in (self.a,self.b,self.k)) and self.a>self.b>0):
            raise ValueError('Require finite a>b>0 and finite slope')

    @property
    def S(self):
        return self.a**2*self.k**2+self.b**2

    @property
    def critical(self):
        return sqrt(self.S)

    def count(self,m):
        if not isfinite(m):
            raise ValueError('Intercept must be finite')
        if isclose(m*m,self.S,rel_tol=1e-12,abs_tol=1e-12):
            return 1
        return 2 if m*m<self.S else 0

    def intersections(self,m):
        count=self.count(m)
        if count==0:
            return []
        center=-self.a**2*self.k*m/self.S
        if count==1:
            return [(center,self.k*center+m)]
        offset=self.a*self.b*sqrt(self.S-m*m)/self.S
        return [(x,self.k*x+m) for x in (center-offset,center+offset)]

    def tangent(self,sign=1):
        if sign not in (-1,1):
            raise ValueError('Tangent sign must be ±1')
        m=sign*self.critical
        return m,(-self.a**2*self.k/m,self.b**2/m)

    def general_count(self,A,B,C):
        if not all(isfinite(v) for v in (A,B,C)) or (A==0 and B==0):
            raise ValueError('Require a valid finite line')
        support=self.a**2*A*A+self.b**2*B*B
        if isclose(C*C,support,rel_tol=1e-12,abs_tol=1e-12):
            return 1
        return 2 if C*C<support else 0


def clip_line(k,m,xlim=3.6,ylim=3.05):
    """Clip an infinite finite-slope line to the display window, without changing it."""
    points=[]
    for x in (-xlim,xlim):
        y=k*x+m
        if abs(y)<=ylim+1e-12:
            points.append((x,y))
    if k!=0:
        for y in (-ylim,ylim):
            x=(y-m)/k
            if abs(x)<=xlim+1e-12 and all(abs(x-u)+abs(y-v)>1e-10 for u,v in points):
                points.append((x,y))
    return points[:2]
