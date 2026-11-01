"""C093's independent, renderer-free confocal conic model.

Knowledge source: this UID's formal 01--06 TeX and meta.json.
Ellipse: x²/a²+y²/b²=1; hyperbola: x²/A²-y²/B²=1.
"""

from dataclasses import dataclass
from math import hypot, isfinite, sqrt


@dataclass(frozen=True)
class ConfocalConics:
    a: float = 4.0
    c: float = 2.0
    A: float = 1.0

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.a, self.c, self.A)):
            raise ValueError("Parameters must be finite")
        if not self.a > self.c > self.A > 0:
            raise ValueError("Require a > c > A > 0")

    @property
    def b(self):
        return sqrt(self.a * self.a - self.c * self.c)

    @property
    def B(self):
        return sqrt(self.c * self.c - self.A * self.A)

    def intersection(self, branch=1, vertical=1):
        if branch not in (-1, 1) or vertical not in (-1, 1):
            raise ValueError("Both signs must be -1 or +1")
        return (branch * self.a * self.A / self.c,
                vertical * self.b * self.B / self.c)

    def distances(self, branch=1, vertical=1):
        x, y = self.intersection(branch, vertical)
        return hypot(x + self.c, y), hypot(x - self.c, y)

    def expected_distances(self, branch=1):
        if branch not in (-1, 1):
            raise ValueError("Branch must be -1 or +1")
        return self.a + branch * self.A, self.a - branch * self.A

    def residuals(self, point):
        x, y = point
        return (x*x / self.a**2 + y*y / self.b**2 - 1,
                x*x / self.A**2 - y*y / self.B**2 - 1)

    def hyperbola_point(self, y, branch=1):
        if branch not in (-1, 1):
            raise ValueError("Branch must be -1 or +1")
        return branch * self.A * sqrt(1 + y*y / self.B**2), y

    def visible_hyperbola_y_limit(self, x_limit=4.5, y_limit=3.65):
        if x_limit <= self.A or y_limit <= 0:
            raise ValueError("Viewport must include the vertices")
        return min(y_limit, self.B * sqrt((x_limit / self.A)**2 - 1))


# Durations in seconds, matching the Scene's play/wait calls. The branch switch
# is a selection between distinct common points, never a path through the gap.
KEY_TIMES = {
    "opening": 0.4,
    "right_radii": 2.1,
    "sum_and_difference": 4.0,
    "A_min": 7.5,
    "A_max": 11.3,
    "A_one": 14.5,
    "left_branch": 17.0,
    "general_formula": 20.0,
    "loop_reset": 21.3,
}
