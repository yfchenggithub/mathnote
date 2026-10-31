"""C090: independent exact confocal model, in mathematical coordinates."""
from dataclasses import dataclass
from math import acos, hypot, pi, sin, sqrt


@dataclass(frozen=True)
class ConfocalState:
    c: float
    a: float
    h: float
    x: float
    y: float
    r1: float
    r2: float
    theta: float
    e1: float
    e2: float
    ellipse_term: float
    hyperbola_term: float

    @property
    def reciprocal_sum(self):
        return 1 / self.e1 + 1 / self.e2

    @property
    def upper_bound(self):
        return 2 / sin(self.theta)


def state(h: float, *, c: float = 2.0, a: float = 4.0,
          sx: int = 1, sy: int = 1) -> ConfocalState:
    if not (a > c > h > 0) or sx not in (-1, 1) or sy not in (-1, 1):
        raise ValueError("Require a > c > h > 0 and coordinate signs ±1")
    x = sx * a * h / c
    y = sy * sqrt((a*a-c*c)*(c*c-h*h)) / c
    r1, r2 = hypot(x+c, y), hypot(x-c, y)
    cosine = (r1*r1+r2*r2-4*c*c)/(2*r1*r2)
    theta = acos(max(-1.0, min(1.0, cosine)))
    e1, e2 = c/a, c/h
    return ConfocalState(c, a, h, x, y, r1, r2, theta, e1, e2,
                         (1-cosine)/(2*e1*e1),
                         (1+cosine)/(2*e2*e2))


def motion_h(time: float) -> float:
    """Full rendered timeline, including pauses and a continuous loop."""
    from math import cos
    for start, end, h0, h1 in ((1.5,4.5,.6,1.65), (5.5,8.5,1.65,.6),
                              (11,14,.6,1.65), (14.5,16,1.65,1),
                              (21,23,1,.6)):
        if start <= time <= end:
            t = (time-start)/(end-start)
            return h0+(h1-h0)*(1-cos(pi*t))/2
    if time < 1.5 or 8.5 < time < 11 or time > 23:
        return .6
    if 4.5 < time < 5.5 or 14 < time < 14.5:
        return 1.65
    return 1.0
