from math import sqrt,cos,sin,cosh,sinh
def params(kind,t):
    if kind=='ellipse':return 3.,t,sqrt(9-t*t)
    if kind=='hyperbola':return 2.,t,sqrt(4+t*t)
    return 0.,0.,t/2
def endpoints(kind,t):
    a,b,c=params(kind,t);h=t if kind=='parabola' else b*b/a
    return (c,h),(c,-h)
def curve(kind,t,u,s=1):
    a,b,c=params(kind,t)
    if kind=='ellipse':return a*cos(u),b*sin(u)
    if kind=='hyperbola':return s*a*cosh(u),b*sinh(u)
    return u*u/(2*t),u
