"""C003 ellipse geometry, in unscaled mathematical coordinates."""
from dataclasses import dataclass
from math import atan2, cos, hypot, sin, sqrt


@dataclass(frozen=True)
class Ellipse:
    a: float = 3.0
    b: float = 2.0

    def __post_init__(self):
        if not self.a > self.b > 0:
            raise ValueError("Require a > b > 0")

    @property
    def c(self):
        return sqrt(self.a**2 - self.b**2)

    def point(self, t):
        return self.a * cos(t), self.b * sin(t)

    def angle(self, t):
        """Angle of the two actual focal rays; stable at major-axis vertices."""
        x, y = self.point(t)
        u, v = (-self.c - x, -y), (self.c - x, -y)
        return atan2(abs(u[0] * v[1] - u[1] * v[0]),
                     u[0] * v[0] + u[1] * v[1])

    def half_tangent(self, t):
        return self.c * abs(self.point(t)[1]) / self.b**2

    @property
    def maximum(self):
        return 2 * atan2(self.c, self.b)

    def focal_sum(self, t):
        x, y = self.point(t)
        return hypot(x + self.c, y) + hypot(x - self.c, y)
