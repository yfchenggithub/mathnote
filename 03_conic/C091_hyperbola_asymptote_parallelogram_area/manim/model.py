"""Independent C091 geometry, derived from the formal six TeX sections."""
from dataclasses import dataclass
from math import cosh, sinh


@dataclass(frozen=True)
class State:
    p: tuple[float, float]
    q: tuple[float, float]
    r: tuple[float, float]
    area: float


def from_point(x: float, y: float, a: float = 3, b: float = 2) -> State:
    if a <= 0 or b <= 0:
        raise ValueError("a and b must be positive")
    q = ((x + a*y/b)/2, (b*x/a + y)/2)
    r = ((x - a*y/b)/2, (-b*x/a + y)/2)
    return State((x, y), q, r, abs(q[0]*r[1] - q[1]*r[0]))


def on_hyperbola(t: float, a: float = 3, b: float = 2, branch: int = 1) -> State:
    if branch not in (-1, 1):
        raise ValueError("branch must be -1 or 1")
    return from_point(branch*a*cosh(t), branch*b*sinh(t), a, b)
