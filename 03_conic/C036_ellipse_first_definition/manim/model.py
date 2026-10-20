from math import sin,cos,sinh,cosh,sqrt,hypot
KIND='ellipse'
a,b=(3.,2.) if KIND=='ellipse' else (1.5,1.)
c=sqrt(a*a-b*b) if KIND=='ellipse' else sqrt(a*a+b*b)
def point(t,branch=1):
    return (a*cos(t),b*sin(t)) if KIND=='ellipse' else (branch*a*cosh(t),b*sinh(t))
def distances(t,branch=1):
    x,y=point(t,branch); return hypot(x+c,y),hypot(x-c,y)
def invariant(t,branch=1):
    r,s=distances(t,branch); return r+s if KIND=='ellipse' else abs(r-s)
