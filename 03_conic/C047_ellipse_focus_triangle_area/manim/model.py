from math import sin,cos,sinh,cosh,sqrt,hypot,acos
KIND='ellipse'
a,b=(3.,2.) if KIND=='ellipse' else (1.5,1.)
c=sqrt(a*a-b*b) if KIND=='ellipse' else sqrt(a*a+b*b)
e=c/a
def point(t): return (a*cos(t),b*sin(t)) if KIND=='ellipse' else (a*cosh(t),b*sinh(t))
def state(t):
    x,y=point(t); r1=hypot(x+c,y); r2=hypot(x-c,y)
    z=((x+c)*(x-c)+y*y)/(r1*r2)
    angle=acos(max(-1.,min(1.,z)))
    return dict(r1=r1,r2=r2,area=c*abs(y),angle=angle)
