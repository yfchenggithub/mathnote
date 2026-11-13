"""P055: reflection of the fixed direction (2,1) in a rotating mirror."""
from math import cos, sin, atan2, pi

ORIGINAL = (2.0, 1.0)
THETA = atan2(1, 2)
VERTICAL_ALPHA = (pi / 2 + THETA) / 2

def reflect(v, alpha):
    x, y = v
    return (cos(2*alpha)*x + sin(2*alpha)*y,
            sin(2*alpha)*x - cos(2*alpha)*y)

def slope(v):
    return None if abs(v[0]) < 1e-10 else v[1]/v[0]
