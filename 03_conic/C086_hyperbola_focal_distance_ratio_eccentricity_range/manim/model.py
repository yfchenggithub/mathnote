"""C086 independent Euclidean model; no rendering dependencies."""
from math import hypot, sqrt, isfinite


def radii(a, ratio):
    if not isfinite(a) or a <= 0 or not isfinite(ratio) or ratio <= 0 or ratio == 1:
        raise ValueError("a>0, ratio>0, ratio!=1 required")
    unit = 2 * a / abs(ratio - 1)
    return ratio * unit, unit


def intersection(a, c, ratio):
    """Ordered upper/lower intersections, one external tangency, or empty."""
    if not isfinite(c) or c <= a:
        raise ValueError("nondegenerate hyperbola requires c>a")
    r1, r2 = radii(a, ratio)
    if 2*c > r1+r2 + 1e-10:
        return []
    x = (r1*r1-r2*r2)/(4*c)
    y2 = r1*r1-(x+c)**2
    if abs(2*c-r1-r2) <= 1e-10:
        return [(x, 0.0)]
    if y2 <= 0:
        raise ArithmeticError("inconsistent circle intersection")
    return [(x, sqrt(y2)), (x, -sqrt(y2))]


def snapshot(a, c, ratio):
    points = intersection(a, c, ratio)
    r1, r2 = radii(a, ratio)
    return dict(a=a, c=c, ratio=ratio, r1=r1, r2=r2,
                b2=c*c-a*a, e=c/a, points=points,
                count=len(points), base=2*c)


def residuals(state):
    a, c, b2 = state['a'], state['c'], state['b2']
    rows = []
    for x, y in state['points']:
        p1, p2 = hypot(x+c, y), hypot(x-c, y)
        rows.append([abs(p1-state['r1']), abs(p2-state['r2']),
                     abs(p1/p2-state['ratio']), abs(abs(p1-p2)-2*a),
                     abs(x*x/(a*a)-y*y/b2-1)])
    return rows
