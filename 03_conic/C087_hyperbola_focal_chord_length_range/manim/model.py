"""Independent metric model for C087; no rendering dependencies."""
from math import cos, sin, sqrt, hypot, atan2, pi


def snapshot(theta, a=3.0, b=4.0):
    if a <= 0 or b <= 0:
        raise ValueError('a and b must be positive')
    c = hypot(a, b)
    q, v = cos(theta), sin(theta)
    d = a*a-c*c*q*q
    if abs(d) < 1e-10:
        rho = -b*b/(2*c*q)
        return dict(a=a, b=b, c=c, theta=theta, kind='boundary',
                    points=[(c+rho*q, rho*v)], length=None, scale=.4)
    # Signed distances along (cos theta, sin theta), derived from the quadratic.
    rhos = [-b*b/(c*q-a), -b*b/(c*q+a)]
    points = [(c+r*q, r*v) for r in rhos]
    length = hypot(points[0][0]-points[1][0], points[0][1]-points[1][1])
    # Uniform scale on both axes; every finite endpoint stays in the viewport.
    extent = max(abs(x-1) for x,y in points)
    height = max(abs(y) for x,y in points)
    scale = min(.4, 3.1/max(extent, 1), 3.1/max(height, 1))
    return dict(a=a, b=b, c=c, theta=theta,
                kind='same' if d > 0 else 'opposite',
                points=points, rhos=rhos, length=length, scale=scale)


def screen(point, scale):
    x, y = point
    return ((x-1)*scale, 1.2+y*scale, 0)


CRITICAL = atan2(4, 3)


def sampling_angles():
    """All planned motions, sampled more densely than the rendered timeline."""
    for start, stop in [(0, pi/6), (pi/6, 0),
                        (78*pi/180, pi/2), (pi/2, 102*pi/180),
                        (102*pi/180, pi/2), (pi/6, 50*pi/180)]:
        for i in range(301):
            yield start+(stop-start)*i/300
