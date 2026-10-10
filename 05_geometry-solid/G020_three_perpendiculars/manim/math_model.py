"""Exact world-coordinate contract for the G020 three-perpendiculars lesson.

The formal plane is z=0.  A is on its positive x-axis, P is vertically
above O, and the demonstrated in-plane line passes through A.  Passing
through A is an example choice, not a new precondition of the theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, radians, sin, sqrt

Vec3 = tuple[float, float, float]


def add(u: Vec3, v: Vec3) -> Vec3:
    return (u[0] + v[0], u[1] + v[1], u[2] + v[2])


def subtract(u: Vec3, v: Vec3) -> Vec3:
    return (u[0] - v[0], u[1] - v[1], u[2] - v[2])


def scale(k: float, u: Vec3) -> Vec3:
    return (k * u[0], k * u[1], k * u[2])


def dot(u: Vec3, v: Vec3) -> float:
    return sum(x * y for x, y in zip(u, v))


def norm(u: Vec3) -> float:
    return sqrt(dot(u, u))


def unit(u: Vec3) -> Vec3:
    length = norm(u)
    if length == 0:
        raise ValueError("zero direction")
    return scale(1 / length, u)


def project_alpha(point: Vec3) -> Vec3:
    """Orthogonal projection onto alpha: z=0."""
    return (point[0], point[1], 0.0)


@dataclass(frozen=True)
class G020State:
    a: float
    height: float
    line_angle_deg: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.a, self.height, self.line_angle_deg)):
            raise ValueError("parameters must be finite")
        if self.a <= 0 or self.height <= 0:
            raise ValueError("A must differ from O and P must be outside alpha")

    @property
    def O(self) -> Vec3:
        return (0.0, 0.0, 0.0)

    @property
    def A(self) -> Vec3:
        return (self.a, 0.0, 0.0)

    @property
    def P(self) -> Vec3:
        return (0.0, 0.0, self.height)

    @property
    def line_direction(self) -> Vec3:
        angle = radians(self.line_angle_deg)
        return (cos(angle), sin(angle), 0.0)

    @property
    def OA(self) -> Vec3:
        return subtract(self.A, self.O)

    @property
    def AP(self) -> Vec3:
        return subtract(self.A, self.P)

    @property
    def PO(self) -> Vec3:
        return subtract(self.O, self.P)

    def point_on_l(self, t: float) -> Vec3:
        return add(self.A, scale(t, self.line_direction))

    def point_on_PA(self, t: float) -> Vec3:
        """t=0 is P; t=1 is A."""
        return add(self.P, scale(t, subtract(self.A, self.P)))

    def projected_point_on_PA(self, t: float) -> Vec3:
        return project_alpha(self.point_on_PA(t))

    @property
    def plane_dot(self) -> float:
        return dot(self.line_direction, self.OA)

    @property
    def space_dot(self) -> float:
        return dot(self.line_direction, self.AP)

    def is_perpendicular(self, tolerance: float = 1e-10) -> bool:
        return abs(self.plane_dot) <= tolerance and abs(self.space_dot) <= tolerance

    def right_angle_corners(self, with_space_line: bool, size: float = 0.32) -> tuple[Vec3, Vec3, Vec3]:
        """Three corners of the actual 3D 90-degree marker at A."""
        if not self.is_perpendicular():
            raise ValueError("right-angle marker requires true perpendicularity")
        first = unit(subtract(self.P, self.A) if with_space_line else subtract(self.O, self.A))
        second = self.line_direction
        return (
            add(self.A, scale(size, first)),
            add(self.A, scale(size, add(first, second))),
            add(self.A, scale(size, second)),
        )


INITIAL = G020State(a=2.8, height=1.6, line_angle_deg=48.0)
PERPENDICULAR = G020State(a=2.8, height=1.6, line_angle_deg=90.0)
RAISED = G020State(a=2.8, height=3.0, line_angle_deg=90.0)
