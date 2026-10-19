"""C008 independent point-form tangent and polar geometry."""
from dataclasses import dataclass
from math import cos,isclose,isfinite,sin,sqrt


@dataclass(frozen=True)
class PointTangentModel:
    a: float=2.
    b: float=1.

    def __post_init__(self):
        if not(all(isfinite(v) for v in (self.a,self.b)) and self.a>self.b>0):
            raise ValueError('Require finite a>b>0')

    def point(self,t):
        return self.a*cos(t),self.b*sin(t)

    def position(self,p):
        return (p[0]/self.a)**2+(p[1]/self.b)**2

    def tangent_at(self,p):
        if not isclose(self.position(p),1,rel_tol=1e-11,abs_tol=1e-11):
            raise ValueError('Tangent point must lie on the ellipse')
        return p[0]/self.a**2,p[1]/self.b**2,1.

    def tangent(self,t):
        return self.tangent_at(self.point(t))

    def polar(self,p):
        if p==(0,0):
            return None  # 0=1 is not a finite-plane line.
        return p[0]/self.a**2,p[1]/self.b**2,1.

    def contacts_from(self,p):
        u,v=p[0]/self.a,p[1]/self.b
        S=u*u+v*v
        if isclose(S,1,rel_tol=1e-12,abs_tol=1e-12):
            return [p]
        if S<1:
            return []
        factor=sqrt(S-1)/S
        return [(self.a*(u/S-sign*v*factor),self.b*(v/S+sign*u*factor)) for sign in (-1,1)]


def clip_line(A,B,C,xmax=2.75,ymax=2.25):
    """Actual Ax+By=C clipped to a finite drawing window; handles vertical lines."""
    if A==0 and B==0:
        raise ValueError('Not a line')
    points=[]
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
