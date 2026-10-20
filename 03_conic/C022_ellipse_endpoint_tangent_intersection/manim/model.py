"""C022: independently compute tangent intersections and polygon area."""
from dataclasses import dataclass
from math import sin, cos, isfinite


@dataclass(frozen=True)
class EndpointModel:
    a: float = 3
    b: float = 2

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.a, self.b)) or not self.a > self.b > 0:
            raise ValueError('Require finite a > b > 0')

    def point(self, t):
        if not isfinite(t):
            raise ValueError('Parameter must be finite')
        return self.a*cos(t), self.b*sin(t)

    def state(self, t):
        p = self.point(t)
        if abs(p[1]/self.b) < 1e-12:
            raise ValueError('Major-axis vertices do not define two unique intersections')
        A, B = p[0]/self.a**2, p[1]/self.b**2
        p1 = (-self.a, (1+A*self.a)/B)
        p2 = (self.a, (1-A*self.a)/B)
        vertices = ((-self.a, 0), p1, p2, (self.a, 0))
        # Shoelace area, independently of the claimed trapezoid formula.
        twice_area = sum(vertices[i][0]*vertices[(i+1)%4][1]-vertices[(i+1)%4][0]*vertices[i][1] for i in range(4))
        h1, h2 = abs(p1[1]), abs(p2[1])
        return dict(p=p, p1=p1, p2=p2, vertices=vertices, h1=h1, h2=h2,
                    product=h1*h2, area=abs(twice_area)/2, k=-A/B, m=1/B)

    def tangent_ends(self, t, xmin=-3.6, xmax=3.6):
        s = self.state(t)
        return ((xmin, s['k']*xmin+s['m']), (xmax, s['k']*xmax+s['m']))
