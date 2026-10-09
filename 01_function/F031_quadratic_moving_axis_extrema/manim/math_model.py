"""Independent F031 mathematics for a fixed interval and a moving axis.

This is one valid subfamily of the formal f(x)=ax²+bx+c:
f_h(x)=a(x-h)²+k, b=-2ah, c=ah²+k. The interval and a,k stay fixed.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose


TOL = 1e-14


@dataclass(frozen=True)
class QuadraticSpec:
    left: float
    right: float
    a: float
    h: float
    k: float = 0.0

    def __post_init__(self) -> None:
        if not self.left < self.right:
            raise ValueError("a nondegenerate closed interval is required")
        if self.a == 0:
            raise ValueError("F031 requires a nonzero quadratic coefficient")

    @property
    def midpoint(self) -> float:
        return (self.left + self.right) / 2

    @property
    def coefficients(self) -> tuple[float, float, float]:
        return self.a, -2 * self.a * self.h, self.a * self.h**2 + self.k

    def value(self, x: float) -> float:
        return self.a * (x - self.h) ** 2 + self.k


@dataclass(frozen=True)
class ExtremumState:
    vertex: tuple[float, float]
    left_value: float
    right_value: float
    minimum_value: float
    maximum_value: float
    minimum_points: tuple[float, ...]
    maximum_points: tuple[float, ...]
    nearest_points: tuple[float, ...]
    farthest_points: tuple[float, ...]
    axis_case: str


def _near(a: float, b: float) -> bool:
    return isclose(a, b, rel_tol=0, abs_tol=TOL)


def _nearest_and_farthest(spec: QuadraticSpec) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Classify by distance to the axis, independently of function values."""
    left, right, h = spec.left, spec.right, spec.h
    nearest = (left,) if h <= left else (right,) if h >= right else (h,)
    dl, dr = abs(left - h), abs(right - h)
    farthest = (left, right) if _near(dl, dr) else (left,) if dl > dr else (right,)
    return nearest, farthest


def analytic_state(spec: QuadraticSpec) -> ExtremumState:
    nearest, farthest = _nearest_and_farthest(spec)
    min_points, max_points = (nearest, farthest) if spec.a > 0 else (farthest, nearest)
    axis_case = (
        "left" if spec.h < spec.left else
        "at_left" if _near(spec.h, spec.left) else
        "left_half" if spec.h < spec.midpoint else
        "midpoint" if _near(spec.h, spec.midpoint) else
        "right_half" if spec.h < spec.right else
        "at_right" if _near(spec.h, spec.right) else "right"
    )
    return ExtremumState(
        vertex=(spec.h, spec.k),
        left_value=spec.value(spec.left),
        right_value=spec.value(spec.right),
        minimum_value=spec.value(min_points[0]),
        maximum_value=spec.value(max_points[0]),
        minimum_points=min_points,
        maximum_points=max_points,
        nearest_points=nearest,
        farthest_points=farthest,
        axis_case=axis_case,
    )


def candidate_extrema(spec: QuadraticSpec) -> tuple[float, tuple[float, ...], float, tuple[float, ...]]:
    """Independent check: evaluate endpoints and any interior stationary point.

    Uses the expanded polynomial and b/(2a), rather than analytic_state's
    distance classification or QuadraticSpec.value.
    """
    a, b, c = spec.coefficients
    stationary = -b / (2 * a)
    candidates = [spec.left, spec.right]
    if spec.left < stationary < spec.right:
        candidates.append(stationary)
    values = [(x, a * x * x + b * x + c) for x in candidates]
    low = min(v for _, v in values)
    high = max(v for _, v in values)
    low_points = tuple(sorted(x for x, v in values if _near(v, low)))
    high_points = tuple(sorted(x for x, v in values if _near(v, high)))
    return low, low_points, high, high_points


def assert_independent_agreement(spec: QuadraticSpec) -> None:
    state = analytic_state(spec)
    low, low_points, high, high_points = candidate_extrema(spec)
    assert isclose(state.minimum_value, low, rel_tol=0, abs_tol=1e-10)
    assert isclose(state.maximum_value, high, rel_tol=0, abs_tol=1e-10)
    assert len(state.minimum_points) == len(low_points)
    assert len(state.maximum_points) == len(high_points)
    assert all(isclose(x, y, rel_tol=0, abs_tol=1e-10)
               for x, y in zip(state.minimum_points, low_points))
    assert all(isclose(x, y, rel_tol=0, abs_tol=1e-10)
               for x, y in zip(state.maximum_points, high_points))
