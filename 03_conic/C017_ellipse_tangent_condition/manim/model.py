"""Independent finite-slope line / ellipse model for C017."""
from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class EllipseLine:
    a: float = 5.0
    b: float = 3.0
    k: float = 0.8

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.a, self.b, self.k)):
            raise ValueError('Parameters must be finite')
        if not self.a > self.b > 0:
            raise ValueError('Require a > b > 0')

    @property
    def threshold(self):
        return self.a**2 * self.k**2 + self.b**2

    @property
    def tangent_intercepts(self):
        t = sqrt(self.threshold)
        return (-t, t)

    def gap(self, m):
        if not isfinite(m):
            raise ValueError('Intercept must be finite')
        return self.threshold - m*m

    def relation(self, m):
        gap = self.gap(m)
        if abs(gap) <= 1e-12 * max(self.threshold, m*m, 1):
            return 'tangent'
        return 'secant' if gap > 0 else 'disjoint'

    def discriminant(self, m):
        return 4*self.a**2*self.b**2*self.gap(m)

    def intersections(self, m):
        state = self.relation(m)
        if state == 'disjoint':
            return ()
        center = -self.a**2*self.k*m/self.threshold
        if state == 'tangent':
            return ((center, self.k*center+m),)
        shift = self.a*self.b*sqrt(self.gap(m))/self.threshold
        return tuple((x, self.k*x+m) for x in (center-shift, center+shift))

    def contact(self, m):
        if self.relation(m) != 'tangent':
            raise ValueError('Contact formula requires tangency')
        return (-self.a**2*self.k/m, self.b**2/m)

    def clipped_line(self, m, bounds=(-6.2, 6.2, -5.3, 5.3)):
        """Clip y=kx+m to the mathematical viewing rectangle."""
        self.gap(m)
        xmin, xmax, ymin, ymax = bounds
        points = []
        for x in (xmin, xmax):
            y = self.k*x+m
            if ymin-1e-10 <= y <= ymax+1e-10:
                points.append((x, y))
        if self.k != 0:
            for y in (ymin, ymax):
                x = (y-m)/self.k
                if xmin-1e-10 <= x <= xmax+1e-10:
                    p = (x, y)
                    if not any(abs(x-q[0])+abs(y-q[1]) < 1e-9 for q in points):
                        points.append(p)
        return tuple(points[:2])
