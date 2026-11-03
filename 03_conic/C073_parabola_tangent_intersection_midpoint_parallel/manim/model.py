"""C073 independent model: y^2=2px, distinct tangent points."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    p: float
    a: float
    b: float

    def __post_init__(self):
        if self.p == 0 or self.a == self.b:
            raise ValueError('Require p != 0 and distinct tangent points')

    def point(self, y):
        return (y*y/(2*self.p), y)

    @property
    def A(self):
        return self.point(self.a)

    @property
    def B(self):
        return self.point(self.b)

    @property
    def M(self):
        return (self.a*self.b/(2*self.p), (self.a+self.b)/2)

    @property
    def N(self):
        return ((self.a*self.a+self.b*self.b)/(4*self.p), (self.a+self.b)/2)

    def tangent_segment(self, y0, bounds=(-2.5, 5.0, -2.65, 4.65)):
        """Clip x=(y0/p)y-y0^2/(2p), including vertical vertex tangent."""
        left, right, bottom, top = bounds
        slope=y0/self.p
        intercept=-y0*y0/(2*self.p)
        pts=[]
        for y in (bottom,top):
            x=slope*y+intercept
            if left-1e-9 <= x <= right+1e-9:
                pts.append((x,y))
        if slope:
            for x in (left,right):
                y=(x-intercept)/slope
                if bottom-1e-9 <= y <= top+1e-9:
                    pts.append((x,y))
        unique=[]
        for pt in pts:
            if not any(abs(pt[0]-q[0])+abs(pt[1]-q[1]) < 1e-8 for q in unique):
                unique.append(pt)
        if len(unique)!=2:
            raise ValueError('Tangent does not cross viewport in two endpoints')
        return tuple(unique)


@dataclass(frozen=True)
class UpwardConfiguration(Configuration):
    """x^2=2py; a and b are the tangent points' x coordinates."""

    def point(self, x):
        return (x, x*x/(2*self.p))

    @property
    def M(self):
        return ((self.a+self.b)/2, self.a*self.b/(2*self.p))

    @property
    def N(self):
        return ((self.a+self.b)/2, (self.a*self.a+self.b*self.b)/(4*self.p))

    def tangent_segment(self, x0, bounds=(-3.0,3.5,-2.2,3.8)):
        left,right,bottom,top=bounds
        swapped=Configuration(self.p,self.a,self.b).tangent_segment(x0,(bottom,top,left,right))
        return tuple((y,x) for x,y in swapped)
