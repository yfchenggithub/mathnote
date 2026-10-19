"""Independent C004 model: angle subtended by the major-axis endpoints."""
from dataclasses import dataclass
from math import atan, atan2, cos, isfinite, pi, sin


@dataclass(frozen=True)
class VertexAngleModel:
    a: float = 2.0
    b: float = 1.0

    def __post_init__(self):
        if not (isfinite(self.a) and isfinite(self.b) and self.a > self.b > 0):
            raise ValueError('Require finite a > b > 0')

    def point(self, t):
        return self.a*cos(t), self.b*sin(t)

    @staticmethod
    def admissible(t):
        # Treat floating-point representations of k*pi as the excluded endpoints.
        return isfinite(t) and abs(sin(t)) > 1e-12

    def angle(self, t):
        """Interior ray angle computed from actual geometry, never a line's acute angle."""
        if not self.admissible(t):
            return None
        x, y = self.point(t)
        u, v = (-self.a-x, -y), (self.a-x, -y)
        return atan2(abs(u[0]*v[1]-u[1]*v[0]), u[0]*v[0]+u[1]*v[1])

    def formula_angle(self, t):
        if not self.admissible(t):
            return None
        y = abs(self.point(t)[1])
        return pi/2 + atan((self.a**2-self.b**2)*y/(2*self.a*self.b**2))

    @property
    def maximum(self):
        return 2*atan(self.a/self.b)

    def area(self, t):
        return self.a*abs(self.point(t)[1])


# Two open arcs, not an orbit through the excluded vertices.
EDGE = 0.14
UPPER = (EDGE, pi/2, pi-EDGE)
LOWER = (pi+EDGE, 3*pi/2, 2*pi-EDGE)
