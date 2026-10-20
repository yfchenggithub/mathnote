"""C018's independent point, chord-limit and implicit tangent model."""
from dataclasses import dataclass
from math import cos, sin, isfinite, hypot


@dataclass(frozen=True)
class Ellipse:
    a: float = 3
    b: float = 2

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.a, self.b)) or not self.a > self.b > 0:
            raise ValueError('Require finite a > b > 0')

    def point(self, t):
        if not isfinite(t):
            raise ValueError('Angle must be finite')
        return (self.a*cos(t), self.b*sin(t))

    def tangent(self, t):
        x, y = self.point(t)
        return (x/self.a**2, y/self.b**2, 1.0)

    def chord(self, t, s):
        """Ax+By=C; continuous limiting tangent when s=t.

        The storyboard uses |s-t| <= pi/3, so endpoints never form an
        antipodal pair or differ by a full revolution.
        """
        self.point(t)
        self.point(s)
        mid = (t+s)/2
        return (cos(mid)/self.a, sin(mid)/self.b, cos((s-t)/2))

    def support_value(self, t, s):
        A, B, _ = self.tangent(t)
        x, y = self.point(s)
        return A*x+B*y

    def clipped(self, coefficients, bounds=(-3.75, 3.75, -3.1, 3.1)):
        A, B, C = coefficients
        if not all(isfinite(v) for v in coefficients) or hypot(A, B) == 0:
            raise ValueError('Require a finite nonzero line normal')
        xmin, xmax, ymin, ymax = bounds
        points = []
        def add(x, y):
            if xmin-1e-10 <= x <= xmax+1e-10 and ymin-1e-10 <= y <= ymax+1e-10:
                if not any(hypot(x-p[0], y-p[1]) < 1e-9 for p in points):
                    points.append((x, y))
        if abs(B) > 1e-12:
            for x in (xmin, xmax):
                add(x, (C-A*x)/B)
        if abs(A) > 1e-12:
            for y in (ymin, ymax):
                add((C-B*y)/A, y)
        return tuple(points[:2])
