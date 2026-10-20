"""Independent C019 radial/tangent slopes and exact ellipse geometry."""
from dataclasses import dataclass
from math import cos, sin, sqrt, isfinite, hypot


@dataclass(frozen=True)
class SlopeProductModel:
    a: float = 4
    b: float = 3

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.a, self.b)) or not self.a > self.b > 0:
            raise ValueError('Require finite a > b > 0')

    def point(self, theta):
        if not isfinite(theta):
            raise ValueError('Parameter must be finite')
        return self.a*cos(theta), self.b*sin(theta)

    def tangent(self, theta):
        x, y = self.point(theta)
        return x/self.a**2, y/self.b**2, 1

    def slopes(self, theta):
        x, y = self.point(theta)
        if abs(x/self.a) < 1e-12 or abs(y/self.b) < 1e-12:
            raise ValueError('Slope product is undefined at axis vertices')
        return y/x, -self.b**2*x/(self.a**2*y)

    def measured_product(self, theta):
        radial, tangent = self.slopes(theta)
        return radial*tangent

    @property
    def constant(self):
        return -self.b**2/self.a**2

    @property
    def eccentricity(self):
        return sqrt(1-self.b**2/self.a**2)

    def clipped_tangent(self, theta, bounds=(-4.8, 4.8, -4.2, 4.2)):
        A, B, C = self.tangent(theta)
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
