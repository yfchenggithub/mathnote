"""Exact geometry for the C002 point-to-line distance lesson.

The moving line has C >= 0. All quantities are mathematical coordinates,
independent of Manim's camera or pixel scale.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, sqrt


A, B = 3.0, 4.0
SEMIMAJOR, SEMIMINOR = 2.0, 1.0
NORMAL = hypot(A, B)
R = hypot(SEMIMAJOR * A, SEMIMINOR * B)


@dataclass(frozen=True)
class State:
    c: float
    relation: str
    near: tuple[float, float]
    far: tuple[float, float]
    near_foot: tuple[float, float]
    far_foot: tuple[float, float]
    intersections: tuple[tuple[float, float], ...]
    d_min: float
    d_max: float


def ellipse_value(point: tuple[float, float]) -> float:
    x, y = point
    return (x / SEMIMAJOR) ** 2 + (y / SEMIMINOR) ** 2


def line_value(point: tuple[float, float], c: float) -> float:
    return A * point[0] + B * point[1] + c


def foot(point: tuple[float, float], c: float) -> tuple[float, float]:
    shift = line_value(point, c) / NORMAL**2
    return point[0] - A * shift, point[1] - B * shift


def support_points() -> tuple[tuple[float, float], tuple[float, float]]:
    far = (SEMIMAJOR**2 * A / R, SEMIMINOR**2 * B / R)
    return (-far[0], -far[1]), far


def intersection_points(c: float) -> tuple[tuple[float, float], ...]:
    """Intersect the line with the ellipse via the unit-circle transform."""
    if c > R + 1e-10:
        return ()
    c = min(c, R)
    u0 = -c * SEMIMAJOR * A / R**2
    v0 = -c * SEMIMINOR * B / R**2
    h = sqrt(max(0.0, 1.0 - (c / R) ** 2))
    du, dv = -SEMIMINOR * B / R * h, SEMIMAJOR * A / R * h
    first = (SEMIMAJOR * (u0 + du), SEMIMINOR * (v0 + dv))
    if h < 1e-9:
        return (first,)
    second = (SEMIMAJOR * (u0 - du), SEMIMINOR * (v0 - dv))
    return first, second


def state(c: float) -> State:
    if c < 0:
        raise ValueError("this lesson uses C >= 0")
    near, far = support_points()
    relation = "separate" if c > R + 1e-10 else "tangent" if abs(c - R) <= 1e-10 else "intersect"
    return State(
        c=c, relation=relation, near=near, far=far,
        near_foot=foot(near, c), far_foot=foot(far, c),
        intersections=intersection_points(c),
        d_min=max(0.0, (c - R) / NORMAL),
        d_max=(c + R) / NORMAL,
    )
