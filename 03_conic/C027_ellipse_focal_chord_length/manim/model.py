from math import sin,cos,sqrt,hypot
a,b=3.,2.
c=sqrt(a*a-b*b)
def endpoints(t):
    f=c; u,v=cos(t),sin(t)
    A=u*u/a**2+v*v/b**2; B=2*f*u/a**2; C=f*f/a**2-1
    roots=[(-B+sign*sqrt(B*B-4*A*C))/(2*A) for sign in (-1,1)]
    return tuple((f+r*u,r*v) for r in roots)
def length(t):
    p,q=endpoints(t); return hypot(p[0]-q[0],p[1]-q[1])
