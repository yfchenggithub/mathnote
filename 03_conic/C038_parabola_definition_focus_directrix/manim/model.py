from math import sin,cos,sinh,cosh,sqrt,hypot
KIND='parabola'
if KIND=='ellipse': a,b=2.5,1.5; c=2.; e=c/a; directrix=a*a/c; focus=(c,0)
elif KIND=='hyperbola': a,b=1.5,1.; c=sqrt(a*a+b*b); e=c/a; directrix=a*a/c; focus=(c,0)
else: p=1.; e=1.; directrix=-p/2; focus=(p/2,0)
def point(t):
    if KIND=='ellipse': return a*cos(t),b*sin(t)
    if KIND=='hyperbola': return a*cosh(t),b*sinh(t)
    return t*t/(2*p),t
def foot(t):
    x,y=point(t); return directrix,y
def distances(t):
    x,y=point(t); return hypot(x-focus[0],y),abs(x-directrix)
def ratio(t):
    r,d=distances(t); return r/d
