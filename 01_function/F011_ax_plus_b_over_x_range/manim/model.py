"""F011 mathematics, independent of rendering and other UIDs."""
from math import hypot, sqrt


def value(x, A=1.0, B=1.0):
    if A <= 0 or B <= 0 or x == 0:
        raise ValueError("Require A>0, B>0 and x!=0")
    return A*x+B/x


def extrema(A=1.0, B=1.0):
    if A <= 0 or B <= 0:
        raise ValueError("Require A>0, B>0")
    return sqrt(B/A), 2*sqrt(A*B)


def branch_points(a, b, k=1.0):
    if min(a, b, k) <= 0:
        raise ValueError("Require a,b,k>0")
    return (a, k/a), (-b, -k/b)


def branch_distance(a, b, k=1.0):
    P, Q = branch_points(a, b, k)
    return hypot(P[0]-Q[0], P[1]-Q[1])


def support_distance(k=1.0):
    if k <= 0:
        raise ValueError("Require k>0")
    return 2*sqrt(2*k)


def smooth_path(start, end, t):
    """Same smoothstep interpolation used by the scene's trackers."""
    if not 0 <= t <= 1:
        raise ValueError("Require t in [0,1]")
    f=t*t*(3-2*t)
    return start+(end-start)*f
