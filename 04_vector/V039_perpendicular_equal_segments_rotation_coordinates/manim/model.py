"""V039's independent Euclidean rotation model; no rendering imports."""
from math import cos, sin, pi, hypot

CENTER = (2.0, -1.0)
SOURCE = (5.0, 3.0)

def displacement(center, point):
    return point[0] - center[0], point[1] - center[1]

def rotate(center, point, angle):
    u, v = displacement(center, point)
    return (center[0] + u*cos(angle) - v*sin(angle),
            center[1] + u*sin(angle) + v*cos(angle))

def quarter_turn(center, point, direction):
    if direction not in (-1, 1):
        raise ValueError('direction must be +1 (CCW) or -1 (CW)')
    u, v = displacement(center, point)
    if hypot(u, v) == 0:
        raise ValueError('BP must have positive length')
    return center[0] - direction*v, center[1] + direction*u

def triangle(center=CENTER, source=SOURCE, angle=0.0):
    """Rotate B,H,P as one rigid triangle, H initially the horizontal foot."""
    foot = (source[0], center[1])
    return center, rotate(center, foot, angle), rotate(center, source, angle)

def audit_state(angle, center=CENTER, source=SOURCE):
    b, h, r = triangle(center, source, angle)
    bh = displacement(b, h)
    hr = displacement(h, r)
    bp = displacement(b, source)
    br = displacement(b, r)
    return {
        'angle': angle, 'point': r,
        'length_squared': sum(x*x for x in br),
        'triangle_dot': sum(x*y for x,y in zip(bh,hr)),
        'source_dot_rotated': sum(x*y for x,y in zip(bp,br)),
    }
