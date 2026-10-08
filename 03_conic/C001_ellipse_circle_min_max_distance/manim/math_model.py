"""Exact geometry for the C001 teaching example, independent of Manim.

E: x²/9 + y²/4 = 1; M=(4, 0); Γ has radius r>0.
The general C001 theorem remains in the six formal TeX files.
"""

from __future__ import annotations

from math import cos, hypot, isclose, sin, sqrt

A, B = 3.0, 2.0
M = (4.0, 0.0)
R_FIRST, R_LAST = 1.0, 7.0
Point = tuple[float, float]


def ellipse_point(theta: float) -> Point:
    return (A * cos(theta), B * sin(theta))


def circle_point(radius: float, theta: float) -> Point:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return (M[0] + radius * cos(theta), M[1] + radius * sin(theta))


def center_distance_range() -> tuple[float, float]:
    # PM² = (5/9)x² - 8x + 20, x∈[-3,3]. Its derivative is <0
    # throughout the interval, so the extrema occur at x=3 and x=-3.
    return (R_FIRST, R_LAST)


def minimum_distance(radius: float) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    if radius < R_FIRST:
        return R_FIRST - radius
    if radius > R_LAST:
        return radius - R_LAST
    return 0.0


def maximum_distance(radius: float) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return R_LAST + radius


def intersection_points(radius: float, *, tol: float = 1e-10) -> tuple[Point, ...]:
    """Return true intersections, ordered upper then lower.

    Eliminating y² gives 5x²−72x+180−9r²=0. Only the smaller root
    is in [-3,3] for 1≤r≤7. Endpoints are treated exactly to avoid
    floating-point flicker at the tangent states.
    """
    if radius <= 0:
        raise ValueError("radius must be positive")
    if radius < R_FIRST - tol or radius > R_LAST + tol:
        return ()
    if abs(radius - R_FIRST) <= tol:
        return ((3.0, 0.0),)
    if abs(radius - R_LAST) <= tol:
        return ((-3.0, 0.0),)
    x = (72.0 - sqrt(1584.0 + 180.0 * radius * radius)) / 10.0
    y = B * sqrt(max(0.0, 1.0 - x * x / (A * A)))
    return ((x, y), (x, -y))


def nearest_pair(radius: float) -> tuple[Point, Point]:
    """A minimizing (ellipse point, circle point) pair."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    if radius < R_FIRST:
        return ((3.0, 0.0), (M[0] - radius, 0.0))
    if radius > R_LAST:
        return ((-3.0, 0.0), (M[0] - radius, 0.0))
    point = intersection_points(radius)[0]
    return (point, point)


def farthest_pair(radius: float) -> tuple[Point, Point]:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return ((-3.0, 0.0), (M[0] + radius, 0.0))


def on_ellipse(point: Point, *, tol: float = 1e-8) -> bool:
    x, y = point
    return isclose(x * x / 9.0 + y * y / 4.0, 1.0, abs_tol=tol)


def on_circle(point: Point, radius: float, *, tol: float = 1e-8) -> bool:
    return isclose(hypot(point[0] - M[0], point[1] - M[1]), radius, abs_tol=tol)
