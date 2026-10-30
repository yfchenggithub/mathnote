"""Independent C089 model, in true Cartesian units (no renderer dependency)."""
from dataclasses import dataclass
from math import cosh, sinh, exp, hypot, isfinite


@dataclass(frozen=True)
class TangentState:
    a: float
    b: float
    t: float
    branch: int
    p: tuple[float, float]
    A: tuple[float, float]
    B: tuple[float, float]

    @property
    def area(self):
        return abs(self.A[0]*self.B[1]-self.B[0]*self.A[1])/2

    @property
    def length_product(self):
        return hypot(*self.A)*hypot(*self.B)

    def tangent_residual(self, q):
        return self.p[0]*q[0]/self.a**2-self.p[1]*q[1]/self.b**2-1


def state(t: float, a: float = 1.5, b: float = 1.0, branch: int = 1):
    if not all(isfinite(z) for z in (t,a,b)) or a<=0 or b<=0 or branch not in (-1,1):
        raise ValueError('finite t, positive a,b and branch +/-1 required')
    return TangentState(a,b,t,branch,
        (branch*a*cosh(t),branch*b*sinh(t)),
        (branch*a*exp(t),branch*b*exp(t)),
        (branch*a*exp(-t),-branch*b*exp(-t)))
