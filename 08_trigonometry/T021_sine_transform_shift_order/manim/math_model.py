"""T021-only point and curve model for the two sine transformation paths.

The geometric path state maps a source point (t, sin t) to
    (scale * t + shift, vertical * sin t).
The curve value is derived by inverting that same x map, so the marked point
and every rendered curve sample share one mathematical state.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin


@dataclass(frozen=True)
class Parameters:
    a: float
    omega: float
    phi: float

    def __post_init__(self) -> None:
        if self.a == 0 or self.omega <= 0:
            raise ValueError("T021 requires A != 0 and omega > 0")

    @property
    def amplitude(self) -> float:
        return abs(self.a)

    @property
    def period(self) -> float:
        return 2 * pi / self.omega

    @property
    def first_shift_distance(self) -> float:
        return abs(self.phi)

    @property
    def second_shift_distance(self) -> float:
        return abs(self.phi) / self.omega

    def target(self, x: float) -> float:
        return self.a * sin(self.omega * x + self.phi)


@dataclass(frozen=True)
class CurveState:
    scale: float
    shift: float
    vertical: float = 1.0

    def __post_init__(self) -> None:
        if self.scale <= 0:
            raise ValueError("horizontal scale must remain positive")

    def point(self, t: float) -> tuple[float, float]:
        return self.scale * t + self.shift, self.vertical * sin(t)

    def value(self, x: float) -> float:
        return self.vertical * sin((x - self.shift) / self.scale)


def _fraction(progress: float) -> float:
    if not 0 <= progress <= 1:
        raise ValueError("progress must be in [0, 1]")
    return progress


def baseline() -> CurveState:
    return CurveState(1.0, 0.0)


def first_shift(p: Parameters, progress: float) -> CurveState:
    u = _fraction(progress)
    return CurveState(1.0, -p.phi * u)


def first_scale(p: Parameters, progress: float) -> CurveState:
    u = _fraction(progress)
    scale = 1.0 + (1.0 / p.omega - 1.0) * u
    return CurveState(scale, -p.phi * scale)


def second_scale(p: Parameters, progress: float) -> CurveState:
    u = _fraction(progress)
    scale = 1.0 + (1.0 / p.omega - 1.0) * u
    return CurveState(scale, 0.0)


def second_shift(p: Parameters, progress: float) -> CurveState:
    u = _fraction(progress)
    return CurveState(1.0 / p.omega, -p.phi / p.omega * u)


def horizontal_result(p: Parameters) -> CurveState:
    return CurveState(1.0 / p.omega, -p.phi / p.omega)


def amplitude_scale(p: Parameters, progress: float) -> CurveState:
    u = _fraction(progress)
    base = horizontal_result(p)
    return CurveState(base.scale, base.shift, 1.0 + (p.amplitude - 1.0) * u)


def reflection(p: Parameters, progress: float) -> CurveState:
    """Geometric flip interpolation; intermediate vertical=0 is not a formal A."""
    u = _fraction(progress)
    base = horizontal_result(p)
    vertical = p.amplitude * (1.0 - 2.0 * u) if p.a < 0 else p.amplitude
    return CurveState(base.scale, base.shift, vertical)


DEMO = Parameters(a=-2.0, omega=2.0, phi=pi / 2)
TRACKED_T = pi / 2
