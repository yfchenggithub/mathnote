"""Independent confocal geometry for C092; coordinates have equal scales."""
from dataclasses import dataclass
from math import hypot, sqrt


@dataclass(frozen=True)
class ConfocalPair:
    a: float = 4.0
    c: float = 2.0
    A: float = 1.0

    def __post_init__(self):
        if not self.a > self.c > self.A > 0:
            raise ValueError("Require a > c > A > 0")

    @property
    def b2(self):
        return self.a**2 - self.c**2

    @property
    def B2(self):
        return self.c**2 - self.A**2

    def point(self, sx=1, sy=1):
        if sx not in (-1, 1) or sy not in (-1, 1):
            raise ValueError("Signs must be +1 or -1")
        return sx * self.a * self.A / self.c, sy * sqrt(self.b2 * self.B2) / self.c

    def slopes(self, sx=1, sy=1):
        x, y = self.point(sx, sy)
        return -self.b2*x/(self.a**2*y), self.B2*x/(self.A**2*y)

    def directions(self, sx=1, sy=1):
        return tuple((1/hypot(1,k), k/hypot(1,k)) for k in self.slopes(sx, sy))

    def hyperbola_x(self, y, sign=1):
        return sign * self.A * sqrt(1 + y*y/self.B2)

