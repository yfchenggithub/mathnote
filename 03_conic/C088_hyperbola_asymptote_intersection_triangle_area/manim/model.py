"""C088 independent renderer-free geometry; formal TeX is the fact source."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class AreaModel:
    k: float
    x1: float
    x2: float

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.k, self.x1, self.x2)):
            raise ValueError("finite parameters required")
        if self.k <= 0 or self.x1 == 0 or self.x2 == 0:
            raise ValueError("k>0 and x1*x2!=0 required")

    @property
    def A(self):
        return (self.x1, self.k * self.x1)

    @property
    def B(self):
        return (self.x2, -self.k * self.x2)

    @property
    def area(self):
        return self.k * abs(self.x1 * self.x2)

    @property
    def intercept(self):
        if self.x1 + self.x2 == 0:
            return None
        return 2 * self.x1 * self.x2 / (self.x1 + self.x2)

    @property
    def split_areas(self):
        if self.intercept is None:
            raise ValueError("horizontal AB has no x-axis intercept")
        return tuple(abs(self.intercept * p[1]) / 2 for p in (self.A, self.B))


# Timings are authored with the scene and serve as real-GIF extraction anchors.
KEY_STATES = {
    "start_vertical": 0.6,
    "half_abscissa": 4.7,
    "moving": 6.4,
    "similarity": 12.5,
    "split_area": 16.0,
    "general_formula": 20.0,
}
