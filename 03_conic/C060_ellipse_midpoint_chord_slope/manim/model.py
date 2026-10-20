from math import sin,cos,sinh,cosh
KIND='ellipse'
a,b,p=2.5,1.6,1.
if KIND=='hyperbola': a,b=1.5,1.
def curve(u,sign=1):
    if KIND=='ellipse':return a*cos(u),b*sin(u)
    if KIND=='hyperbola':return sign*a*cosh(u),sign*b*sinh(u)
    return u*u/(2*p),u
def endpoints(t):
    if KIND=='ellipse':return curve(t-.55),curve(t+.55)
    if KIND=='hyperbola':return curve(t+.5),curve(t-.5,-1)
    return curve(t-1),curve(t+1)
def midpoint(t):
    A,B=endpoints(t);return ((A[0]+B[0])/2,(A[1]+B[1])/2)
def slope(t):
    A,B=endpoints(t)
    if abs(A[0]-B[0])<1e-10:raise ValueError('Vertical chord')
    return (A[1]-B[1])/(A[0]-B[0])
