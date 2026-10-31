"""C094 mathematics, independently derived from the formal six TeX sections."""
from dataclasses import dataclass
from math import cos, hypot, isfinite, sin, sqrt


@dataclass(frozen=True)
class ConfocalPair:
    a_e: float = 4.0
    c: float = 2.0
    a_h: float = 1.0

    def __post_init__(self):
        if not all(isfinite(x) for x in (self.a_e, self.c, self.a_h)):
            raise ValueError("finite parameters required")
        if not self.a_e > self.c > self.a_h > 0:
            raise ValueError("nondegenerate confocal pair requires a_e > c > a_h > 0")

    @property
    def b_e(self):
        return sqrt(self.a_e**2 - self.c**2)

    @property
    def b_h(self):
        return sqrt(self.c**2 - self.a_h**2)

    @property
    def positive_point(self):
        return self.a_e * self.a_h / self.c, self.b_e * self.b_h / self.c

    def points(self):
        x, y = self.positive_point
        return ((x, y), (x, -y), (-x, y), (-x, -y))

    def ellipse(self, angle):
        return self.a_e * cos(angle), self.b_e * sin(angle)

    def hyperbola(self, y, branch=1):
        if branch not in (-1, 1):
            raise ValueError("branch must be +/-1")
        return branch * self.a_h * sqrt(1 + y*y / self.b_h**2), y

    def visible_hyperbola_y(self, x_limit=4.3, y_limit=3.8):
        """Fit the true curve in the graph window without screen-edge clipping."""
        if x_limit <= self.a_h or y_limit <= 0:
            raise ValueError("window must contain the hyperbola vertices")
        return min(y_limit,self.b_h*sqrt((x_limit/self.a_h)**2-1))

    def focal_distances(self, point):
        x, y = point
        return hypot(x + self.c, y), hypot(x - self.c, y)

    def residuals(self, point):
        x, y = point
        return (x*x/self.a_e**2 + y*y/self.b_e**2 - 1,
                x*x/self.a_h**2 - y*y/self.b_h**2 - 1)


# The actual sweep is bounded away from all excluded degeneracies.
SWEEP = (1.0, 0.65, 1.65, 1.0)
