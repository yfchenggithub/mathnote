"""Exact ellipse focal-chord model; no layout-dependent coordinates."""

from dataclasses import dataclass
from math import hypot, isclose, sqrt


@dataclass(frozen=True)
class Ellipse:
    a: float = 3.0
    b: float = 2.0

    def __post_init__(self):
        if not self.a > self.b > 0:
            raise ValueError("require a>b>0")

    @property
    def c(self):
        return sqrt(self.a * self.a - self.b * self.b)

    def focus(self, side=1):
        if side not in (-1, 1):
            raise ValueError("side must be -1 or 1")
        return side * self.c, 0.0

    def intersections(self, k=None, side=1):
        """Return two exact-model intersections, sorted by x or y."""
        f, _ = self.focus(side)
        if k is None:
            y = self.b * self.b / self.a
            return ((f, -y), (f, y))
        a2, b2 = self.a ** 2, self.b ** 2
        A = a2 * k * k + b2
        B = -2 * a2 * k * k * f
        C = a2 * k * k * f * f - a2 * b2
        delta = B * B - 4 * A * C
        if delta <= 0:
            raise ArithmeticError("expected two intersections")
        xs = sorted(((-B - sqrt(delta)) / (2 * A),
                     (-B + sqrt(delta)) / (2 * A)))
        return tuple((x, k * (x - f)) for x in xs)

    def formula(self, k=None):
        if k is None:
            return 2 * self.b * self.b / self.a
        return 2 * self.a * self.b * self.b * (1 + k * k) / (
            self.a * self.a * k * k + self.b * self.b)

    def distance(self, k=None, side=1):
        p, q = self.intersections(k, side)
        return hypot(q[0] - p[0], q[1] - p[1])

    def validate_case(self, k, side):
        p, q = self.intersections(k, side)
        f, _ = self.focus(side)
        for x, y in (p, q):
            assert isclose(x*x/self.a**2 + y*y/self.b**2, 1, abs_tol=1e-11)
            if k is None:
                assert isclose(x, f, abs_tol=1e-11)
                assert isclose(abs(y), self.b*self.b/self.a, abs_tol=1e-11)
            else:
                assert isclose(y, k*(x-f), abs_tol=1e-11)
        if k is not None:
            assert isclose((p[0]-f)*(q[1]) - (q[0]-f)*(p[1]),
                           0, abs_tol=1e-11)
            assert isclose(self.distance(k, side),
                           sqrt(1+k*k)*abs(q[0]-p[0]), abs_tol=1e-11)
        assert isclose(self.distance(k, side), self.formula(k), abs_tol=1e-11)
        return {"side": side, "k": k, "P": p, "Q": q,
                "F": (f, 0), "distance": self.distance(k, side),
                "formula": self.formula(k)}


def validation_results():
    e = Ellipse()
    cases = [e.validate_case(k, side) for side in (-1, 1)
             for k in (0, 1, -1, None)]
    a, b, k = e.a, e.b, 1
    c2 = e.c ** 2
    A = a*a*k*k + b*b
    B = -2*a*a*k*k*e.c
    C = a*a*k*k*c2 - a*a*b*b
    delta = B*B-4*A*C
    assert isclose(delta, 4*a*a*b**4*(1+k*k), abs_tol=1e-10)
    assert isclose(sqrt(delta)/A,
                   2*a*b*b*sqrt(1+k*k)/A, abs_tol=1e-11)
    assert isclose(e.formula(1), 48/13, abs_tol=1e-11)
    assert isclose(e.formula(None), 8/3, abs_tol=1e-11)
    # Coefficients of Δ/(4a²) as a polynomial in t=k²:
    # a²t²c² - (a²t+b²)(tc²-b²) = b⁴(1+t).
    coefficients = (b**4, a*a*b*b-b*b*c2, a*a*c2-a*a*c2)
    assert all(isclose(got, want, abs_tol=1e-10) for got, want in
               zip(coefficients, (b**4, b**4, 0)))
    return {"cases": cases, "quadratic": {"A": A, "B": B, "C": C,
             "discriminant": delta}, "discriminant_coefficients": coefficients,
             "example": "48/13",
             "latus_rectum": "8/3"}
