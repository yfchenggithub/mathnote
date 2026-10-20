"""C011: centre-to-point and tangent slopes, independent of rendering."""
import math


def point(t, a=2.0, b=1.0):
    if not a > b > 0:
        raise ValueError('Require a > b > 0')
    return a * math.cos(t), b * math.sin(t)


def tangent(t, a=2.0, b=1.0):
    x, y = point(t, a, b)
    return x / a**2, y / b**2, 1.0


def slopes(t, a=2.0, b=1.0):
    x, y = point(t, a, b)
    radial = None if abs(x) < 1e-10 else y / x
    tangential = None if abs(y) < 1e-10 else -b*b*x/(a*a*y)
    return radial, tangential


def product(t, a=2.0, b=1.0):
    r, s = slopes(t, a, b)
    return None if r is None or s is None else r*s


def clip_line(A, B, C, box=(-2.6, 2.6, -2.1, 2.1)):
    """General-form line, including horizontal and vertical tangents."""
    xmin, xmax, ymin, ymax = box
    hits = []
    if abs(B) > 1e-12:
        for x in (xmin, xmax):
            y = (C-A*x)/B
            if ymin-1e-9 <= y <= ymax+1e-9:
                hits.append((x, y))
    if abs(A) > 1e-12:
        for y in (ymin, ymax):
            x = (C-B*y)/A
            if xmin-1e-9 <= x <= xmax+1e-9:
                if not any(math.hypot(x-u, y-v)<1e-8 for u,v in hits):
                    hits.append((x, y))
    if len(hits) != 2:
        raise ValueError('Line must intersect the viewing rectangle twice')
    return hits
