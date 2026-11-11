"""P033's own Euclidean model; no renderer-dependent mathematics."""
from __future__ import annotations
from dataclasses import dataclass
import math

Point = tuple[float, float]

def distance(u: Point, v: Point) -> float:
    return math.hypot(u[0]-v[0], u[1]-v[1])

def foot(p: Point, u: Point, v: Point) -> Point:
    dx, dy = v[0]-u[0], v[1]-u[1]
    d = dx*dx+dy*dy
    if d == 0:
        raise ValueError('two endpoints must be different')
    t = ((p[0]-u[0])*dx+(p[1]-u[1])*dy)/d
    return (u[0]+t*dx, u[1]+t*dy)

def area(a: Point, b: Point, c: Point) -> float:
    return abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2

@dataclass(frozen=True)
class Triangle:
    A: Point
    B: Point
    C: Point

    def __post_init__(self):
        if area(self.A,self.B,self.C) <= 1e-12:
            raise ValueError('three vertices must not be collinear')

    @property
    def sides(self):
        return (distance(self.B,self.C),distance(self.C,self.A),distance(self.A,self.B))

    @property
    def p(self):
        return sum(self.sides)/2

    @property
    def S(self):
        return area(self.A,self.B,self.C)

    @property
    def I(self):
        a,b,c=self.sides
        return tuple((a*self.A[k]+b*self.B[k]+c*self.C[k])/(a+b+c) for k in (0,1))

    @property
    def r(self):
        return self.S/self.p

    @property
    def feet(self):
        return tuple(foot(self.I,u,v) for u,v in ((self.B,self.C),(self.C,self.A),(self.A,self.B)))

    @property
    def tangent_lengths(self):
        return tuple(self.p-side for side in self.sides)

    @property
    def pieces(self):
        return tuple(area(self.I,u,v) for u,v in ((self.B,self.C),(self.C,self.A),(self.A,self.B)))

def moving_triangle(t: float) -> Triangle:
    """A smooth, nondegenerate round trip; B,C fixed, A moves then returns."""
    return Triangle((9+2*math.sin(2*math.pi*t),12-2*math.sin(math.pi*t)**2),(0,0),(14,0))

def lesson_triangle() -> Triangle:
    return Triangle((9,12),(0,0),(14,0))

def equilateral(side=6.) -> Triangle:
    if side <= 0: raise ValueError('positive side required')
    return Triangle((side/2,math.sqrt(3)*side/2),(0,0),(side,0))

def right_triangle(u=3.,v=4.) -> Triangle:
    if min(u,v) <= 0: raise ValueError('positive legs required')
    return Triangle((0,v),(0,0),(u,0))
