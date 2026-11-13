"""Independent C095 geometry, derived from formal second-intersection formula."""
P = (2, 1)
Q = (2, -1)
M_MIN = 1.25
M_MAX = 2.5

def second_point(k):
    d = .5 - k*k
    if abs(d) < 1e-12:
        raise ValueError('parallel to asymptote: no second finite point')
    h = -2*(1-k)/d
    if abs(h) < 1e-12:
        raise ValueError('tangent at P: repeated point')
    return 2+h, 1+k*h

def secants(m):
    if abs(m) < 1e-12:
        raise ValueError('two identical secants')
    return second_point(m), second_point(-m)

def intercept(m):
    return (2*m*m+1)/(2*m*m-1)
