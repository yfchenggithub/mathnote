"""V033 independent geometry, read against the formal TeX; no renderer dependency."""
from dataclasses import dataclass
from math import isclose

Point = tuple[float, float]
O: Point = (0.0, 0.0)
A: Point = (3.0, 2.0)
B: Point = (2.0, 3.0)
KINDS = ('B_vertical', 'B_horizontal', 'A_vertical', 'A_horizontal')


def determinant(a: Point, b: Point) -> float:
    return a[0] * b[1] - b[0] * a[1]


def area(a: Point, b: Point) -> float:
    return abs(determinant(a, b)) / 2


def triangle_area(p: Point, q: Point, r: Point) -> float:
    return area((q[0]-p[0], q[1]-p[1]), (r[0]-p[0], r[1]-p[1]))


@dataclass(frozen=True)
class Construction:
    kind: str
    start: Point
    other: Point
    intersection: Point
    ratio: float
    base: float
    height: float

    @property
    def internal(self) -> bool:
        return 0 <= self.ratio <= 1

    @property
    def computed_area(self) -> float:
        return self.base * self.height / 2

    @property
    def partial_areas(self) -> tuple[float, float]:
        return (triangle_area(O, self.start, self.intersection),
                triangle_area(self.other, self.start, self.intersection))


def construct(kind: str, a: Point = A, b: Point = B) -> Construction | None:
    if kind not in KINDS:
        raise ValueError(kind)
    start, other = (b, a) if kind.startswith('B') else (a, b)
    vertical = kind.endswith('vertical')
    axis = 0 if vertical else 1
    denominator = other[axis]
    if isclose(denominator, 0, abs_tol=1e-12):
        return None  # Use the axis-aligned OB/OA as the base, never divide by zero.
    t = start[axis] / denominator
    hit = (other[0] * t, other[1] * t)
    base = abs(start[1-axis] - hit[1-axis])
    return Construction(kind, start, other, hit, t, base, abs(denominator))


def moving_b_y(segment: int, alpha: float) -> float:
    if not 0 <= alpha <= 1:
        raise ValueError('alpha must be in [0,1]')
    values = (3.0, 4/3, 0.5, 3.0)
    if segment not in (0, 1, 2):
        raise ValueError(segment)
    return values[segment] * (1-alpha) + values[segment+1] * alpha
