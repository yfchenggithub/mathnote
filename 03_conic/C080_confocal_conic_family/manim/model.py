from math import sqrt,cos,sin,cosh,sinh
c=2.
def params(kind,t):
    return (sqrt(t*t+c*c),t) if kind=='ellipse' else (t,sqrt(c*c-t*t))
def curve(kind,t,u,s=1):
    a,b=params(kind,t)
    return (a*cos(u),b*sin(u)) if kind=='ellipse' else (s*a*cosh(u),b*sinh(u))
