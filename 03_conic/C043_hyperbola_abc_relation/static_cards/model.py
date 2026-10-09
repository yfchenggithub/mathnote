"""Hyperbola geometry, independent of pixels and card layout."""

from dataclasses import dataclass
from fractions import Fraction
from math import cosh, isclose, sinh, sqrt


@dataclass(frozen=True)
class Hyperbola:
    a: Fraction
    b: Fraction

    def __post_init__(self):
        object.__setattr__(self, "a", Fraction(self.a))
        object.__setattr__(self, "b", Fraction(self.b))
        if self.a <= 0 or self.b <= 0:
            raise ValueError("a and b must be positive")

    @property
    def c_squared(self):
        return self.a * self.a + self.b * self.b

    @property
    def c(self):
        return sqrt(float(self.c_squared))

    @property
    def vertices(self):
        return ((-self.a, Fraction(0)), (self.a, Fraction(0)))

    @property
    def foci(self):
        return ((-self.c, 0.0), (self.c, 0.0))

    @property
    def rectangle(self):
        return tuple((x, y) for x, y in ((-self.a, -self.b),
                                           (self.a, -self.b),
                                           (self.a, self.b),
                                           (-self.a, self.b)))

    def branch_point(self, side: int, t: float):
        if side not in (-1, 1):
            raise ValueError("side must be -1 or 1")
        return (side * float(self.a) * cosh(t), float(self.b) * sinh(t))

    def exact_branch_point(self, side: int, u: Fraction):
        """Rational parametrization of either branch; u>0."""
        if side not in (-1, 1) or u <= 0:
            raise ValueError("invalid branch parameter")
        u = Fraction(u)
        return (side * self.a * (u + 1 / u) / 2,
                self.b * (u - 1 / u) / 2)

    def equation_value(self, point):
        x, y = map(Fraction, point)
        return x * x / (self.a * self.a) - y * y / (self.b * self.b)

    def asymptote_y(self, x, sign=1):
        if sign not in (-1, 1):
            raise ValueError("sign must be -1 or 1")
        return sign * self.b * Fraction(x) / self.a


def validation_results():
    checks = {}
    for a, b in ((3, 4), (4, 3), (2, 5)):
        m = Hyperbola(a, b)
        assert m.c_squared == a * a + b * b and m.c > a and m.c > b
        assert m.vertices == ((-a, 0), (a, 0))
        assert isclose(m.foci[1][0] - m.foci[0][0], 2 * m.c)
        assert m.rectangle == ((-a, -b), (a, -b), (a, b), (-a, b))
        assert m.asymptote_y(0) == 0
        for x, y in m.rectangle:
            assert abs(m.asymptote_y(x)) == abs(y)
            assert m.equation_value((x, y)) == 0
        checks[f"parameters, foci, rectangle, asymptotes a={a} b={b}"] = "PASS"
        for side in (-1, 1):
            for u in (Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(3)):
                point = m.exact_branch_point(side, u)
                assert m.equation_value(point) == 1
                assert (point[0] > 0) == (side == 1)
            for t in (-1.1, -0.4, 0, 0.4, 1.1):
                x, y = m.branch_point(side, t)
                assert isclose((x / a) ** 2 - (y / b) ** 2, 1, abs_tol=1e-12)
            checks[f"two branches and signed parameters a={a} b={b} side={side}"] = "PASS"
    m = Hyperbola(4, 3)  # Formal example 1: 9x²-16y²=144.
    assert m.c_squared == 25 and m.c == 5 and m.asymptote_y(4) == 3
    checks["formal example 1: a=4 b=3 c=5"] = "PASS"
    m = Hyperbola(3, 4)  # Formal example 2: one focus (5,0), a=3.
    assert m.c_squared == 25 and m.c == 5 and m.asymptote_y(3) == 4
    checks["formal example 2: a=3 b=4 c=5"] = "PASS"
    return checks
