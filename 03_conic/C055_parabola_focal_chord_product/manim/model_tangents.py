"""C055 focal chord and its two tangents, independently of the renderer.

Knowledge source: 01_statement.tex and the tangent proof in 03_proof.tex.
The chord is x=m*y+p/2. Its two roots are ordered A above, B below.
"""

from dataclasses import dataclass
from math import hypot, isfinite


Point = tuple[float, float]


@dataclass(frozen=True)
class TangentState:
    a: Point
    b: Point
    focus: Point
    intersection: Point
    slope_a: float
    slope_b: float


def tangent_state(m: float, p: float = 2.0) -> TangentState:
    """Return the exact analytic geometry for a finite, non-axial chord."""
    if not isfinite(p) or p <= 0 or not isfinite(m):
        raise ValueError("p must be positive and m must be finite")
    radius = hypot(m, 1.0)
    # This expression avoids cancellation for the shorter focal segment.
    positive_root = p * (m + radius) if m >= 0 else p / (radius - m)
    negative_root = -p * p / positive_root
    a = (positive_root * positive_root / (2 * p), positive_root)
    b = (negative_root * negative_root / (2 * p), negative_root)
    return TangentState(
        a=a,
        b=b,
        focus=(p / 2, 0.0),
        intersection=(-p / 2, p * m),
        slope_a=p / positive_root,
        slope_b=p / negative_root,
    )


def unit_from_to(start: Point, end: Point) -> Point:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = hypot(dx, dy)
    return dx / length, dy / length


def right_angle_vertices(state: TangentState, side: float = 0.24) -> tuple[Point, ...]:
    """Three corners of the square inside angle ATB, using true unit vectors."""
    tx, ty = state.intersection
    ux, uy = unit_from_to(state.intersection, state.a)
    vx, vy = unit_from_to(state.intersection, state.b)
    return (
        (tx + side * ux, ty + side * uy),
        (tx + side * (ux + vx), ty + side * (uy + vy)),
        (tx + side * vx, ty + side * vy),
    )
