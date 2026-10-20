"""C020: distances computed independently from geometry, not the invariant."""
from dataclasses import dataclass
from math import sin, cos, sqrt, hypot, isfinite


@dataclass(frozen=True)
class DistanceProductModel:
    a: float = 4
    b: float = 3

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.a, self.b)) or not self.a > self.b > 0:
            raise ValueError('Require finite a > b > 0')

    @property
    def c(self):
        return sqrt(self.a**2-self.b**2)

    @property
    def foci(self):
        return ((-self.c, 0), (self.c, 0))

    def point(self, t):
        if not isfinite(t):
            raise ValueError('Parameter must be finite')
        return self.a*cos(t), self.b*sin(t)

    def tangent(self, t):
        x, y = self.point(t)
        return x/self.a**2, y/self.b**2, 1.0

    def state(self, t):
        p = self.point(t)
        A, B, _ = self.tangent(t)
        normal_sq = A*A+B*B
        h = (A/normal_sq, B/normal_sq)
        f1, f2 = self.foci
        r1 = hypot(p[0]-f1[0], p[1]-f1[1])
        r2 = hypot(p[0]-f2[0], p[1]-f2[1])
        d = hypot(*h)
        geometric_mean = sqrt(r1*r2)
        return dict(p=p, h=h, r1=r1, r2=r2, d=d,
                    geometric_mean=geometric_mean, product=geometric_mean*d)

    def clipped_tangent(self, t, bounds=(-5, 5, -4.35, 4.35)):
        A, B, C = self.tangent(t)
        xmin, xmax, ymin, ymax = bounds
        points = []
        def append(x, y):
            if xmin-1e-10 <= x <= xmax+1e-10 and ymin-1e-10 <= y <= ymax+1e-10:
                if not any(hypot(x-p[0], y-p[1]) < 1e-9 for p in points):
                    points.append((x, y))
        if abs(B) > 1e-12:
            for x in (xmin, xmax):
                append(x, (C-A*x)/B)
        if abs(A) > 1e-12:
            for y in (ymin, ymax):
                append((C-B*y)/A, y)
        return tuple(points[:2])
