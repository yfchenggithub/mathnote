"""C005: an independently parameterized ellipse family and focal-angle bound."""
from dataclasses import dataclass
from math import asin, atan2, cos, hypot, isfinite, pi, sin, sqrt, tan


@dataclass(frozen=True)
class FocalBoundModel:
    a: float = 5.0
    e: float = .6

    def __post_init__(self):
        if not (isfinite(self.a) and isfinite(self.e) and self.a > 0 and 0 < self.e < 1):
            raise ValueError('Require finite a>0 and 0<e<1')

    @property
    def b(self):
        return self.a*sqrt(1-self.e*self.e)

    @property
    def c(self):
        return self.a*self.e

    def point(self, t):
        return self.a*cos(t), self.b*sin(t)

    def radii(self, t):
        x,y = self.point(t)
        return hypot(x+self.c,y), hypot(x-self.c,y)

    def angle(self, t):
        x,y = self.point(t)
        u,v = (-self.c-x,-y),(self.c-x,-y)
        return atan2(abs(u[0]*v[1]-u[1]*v[0]), u[0]*v[0]+u[1]*v[1])

    def half_sine(self, t):
        return sin(self.angle(t)/2)

    @property
    def maximum(self):
        return 2*asin(self.e)

    def parameter_for_angle(self, target):
        """First-quadrant solution, or None when the target is unattainable."""
        if not 0 <= target < pi:
            raise ValueError('Target must belong to [0, pi)')
        if target > self.maximum+1e-12:
            return None
        normalized_y = self.b/self.c*tan(target/2)
        return asin(min(1.,max(0.,normalized_y)))


START = atan2(.8,.6)  # Formal example P=(3,16/5), a=5,b=4.
RIGHT_THRESHOLD = sqrt(.5)
ANGLE120_THRESHOLD = sqrt(3)/2
