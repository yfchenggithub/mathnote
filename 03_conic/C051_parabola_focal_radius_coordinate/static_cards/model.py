"""Exact rational model for the right-opening parabola y² = 2px."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Parabola:
    p: Fraction

    def __post_init__(self):
        if self.p <= 0:
            raise ValueError("p must be positive")

    @property
    def focus(self):
        return (self.p / 2, Fraction(0))

    @property
    def directrix_x(self):
        return -self.p / 2

    def point(self, y):
        y = Fraction(y)
        return (y * y / (2 * self.p), y)

    def foot(self, point):
        self.assert_on_curve(point)
        return (self.directrix_x, point[1])

    def assert_on_curve(self, point):
        x, y = map(Fraction, point)
        if y * y != 2 * self.p * x:
            raise ValueError("point is not on the parabola")

    def check_geometry(self, point):
        self.assert_on_curve(point)
        x, y = map(Fraction, point)
        f, h = self.focus, self.foot(point)
        radius = x + self.p / 2
        assert x >= 0 and h[0] == self.directrix_x and h[1] == y
        assert (x - f[0]) ** 2 + (y - f[1]) ** 2 == radius ** 2
        assert x - h[0] == radius
        return {"P": (x, y), "F": f, "H": h, "PF": radius, "PH": radius}


def validation_results():
    results = {}
    for p in (Fraction(1, 2), Fraction(2), Fraction(7, 3)):
        model = Parabola(p)
        for y in (Fraction(0), p, -p, 2 * p):
            model.check_geometry(model.point(y))
            results[f"p={p}, y={y}"] = "PASS"
    try:
        Parabola(Fraction(0))
    except ValueError:
        results["reject p=0"] = "PASS"
    else:
        raise AssertionError("p=0 accepted")
    try:
        Parabola(Fraction(2)).check_geometry((4, 3))
    except ValueError:
        results["reject off-curve point"] = "PASS"
    else:
        raise AssertionError("off-curve point accepted")
    example = Parabola(Fraction(2))
    assert example.check_geometry((Fraction(4), Fraction(4)))["PF"] == 5
    assert example.check_geometry(example.point(0))["PF"] == 1
    results["worked example and vertex"] = "PASS"
    return results
