from math import pi,cos,sin
def point(t,a,b): return (a*cos(t),b*sin(t))
def area(a,b):
    if min(a,b)<=0: raise ValueError('Positive semiaxes required')
    return pi*a*b
