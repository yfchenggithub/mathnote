"""C085 independent mathematical model, sourced from this UID's formal TeX."""
from dataclasses import dataclass
from math import hypot, sqrt


@dataclass(frozen=True)
class Configuration:
    a: float = 3.0
    b: float = 4.0

    def __post_init__(self):
        if self.a <= 0 or self.b <= 0:
            raise ValueError('a and b must be positive')

    @property
    def c(self): return hypot(self.a, self.b)
    @property
    def k(self): return self.b / self.a
    @property
    def e(self): return self.c / self.a
    @property
    def t(self): return self.b**2 / (2*self.c)
    @property
    def F(self): return (self.c, 0.0)
    @property
    def M(self): return (self.c-self.t, -self.k*self.t)
    @property
    def N(self): return (self.c/2, -self.k*self.c/2)
    @property
    def fm(self): return self.b**2 / (2*self.a)
    @property
    def mn(self): return self.a/2
    @property
    def ratio(self): return self.b**2/self.a**2

    def curve(self, y):
        return (self.a*sqrt(1+y*y/self.b**2), y)

    def snapshot(self):
        return {key:getattr(self,key) for key in
                ('a','b','c','k','e','t','F','M','N','fm','mn','ratio')}


# The entire motion uses a fixed coordinate scale; it never fits each state.
SCALE = 1.05
ORIGIN = (-3.0, 1.7)


def screen(point):
    x,y=point
    return (ORIGIN[0]+SCALE*x, ORIGIN[1]+SCALE*y, 0.0)


def familiar_points():
    """Same segment lengths as a=3,b=4, with one common display scale."""
    m=Configuration()
    scale=1.38
    left=-(m.fm+m.mn)*scale/2
    return ((left,1,0),(left+m.fm*scale,1,0),(-left,1,0))
