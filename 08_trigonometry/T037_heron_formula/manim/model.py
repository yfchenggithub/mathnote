"""T037: independent side-length model, with Euclidean cross-checks in tests."""
from dataclasses import dataclass
from math import sqrt, hypot, isfinite


def distance(u, v):
    return hypot(u[0]-v[0], u[1]-v[1])


def foot(p, u, v):
    dx, dy = v[0]-u[0], v[1]-u[1]
    k = ((p[0]-u[0])*dx+(p[1]-u[1])*dy)/(dx*dx+dy*dy)
    return u[0]+k*dx, u[1]+k*dy


def coordinate_area(u, v, w):
    return abs((v[0]-u[0])*(w[1]-u[1])-(v[1]-u[1])*(w[0]-u[0]))/2


@dataclass(frozen=True)
class Triangle:
    """a=BC, b=CA, c=AB; A=(0,0), B=(c,0), C above AB."""
    a: float
    b: float
    c: float

    def __post_init__(self):
        sides = (self.a, self.b, self.c)
        if not all(isfinite(x) and x > 0 for x in sides):
            raise ValueError('sides must be positive finite numbers')
        if not all(2*x < sum(sides) for x in sides):
            raise ValueError('strict triangle inequalities are required')

    @property
    def p(self):
        return (self.a+self.b+self.c)/2

    @property
    def factors(self):
        return self.p, self.p-self.a, self.p-self.b, self.p-self.c

    @property
    def S(self):
        p, x, y, z = self.factors
        return sqrt(p*x*y*z)

    @property
    def A(self):
        return (0., 0.)

    @property
    def B(self):
        return (self.c, 0.)

    @property
    def C(self):
        q = (self.b**2+self.c**2-self.a**2)/(2*self.c)
        return q, sqrt(self.b**2-q**2)

    @property
    def I(self):
        return tuple((self.a*self.A[k]+self.b*self.B[k]+self.c*self.C[k])/(2*self.p) for k in (0, 1))

    @property
    def r(self):
        return self.S/self.p

    @property
    def feet(self):
        # Exactly the formal T037 convention: D on BC, E on CA, F on AB.
        return tuple(foot(self.I,u,v) for u,v in ((self.B,self.C),(self.C,self.A),(self.A,self.B)))


def varying_base(c):
    return Triangle(5., 6., c)


def equilateral(ell):
    return Triangle(ell, ell, ell)


def right_triangle(a, b):
    # C is the right-angle vertex; c is the hypotenuse.
    return Triangle(a, b, hypot(a,b))
