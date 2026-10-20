from math import cosh,sinh
KIND='hyperbola'
a,b,p=1.5,1.,1.
def point(t):return (a*cosh(t),b*sinh(t)) if KIND=='hyperbola' else (t*t/(2*p),t)
def tangent(t):
    x,y=point(t)
    return (x/a**2,-y/b**2,1.) if KIND=='hyperbola' else (-p,y,p*x)
def segment(t):
    A,B,C=tangent(t);x,y=point(t);n=(A*A+B*B)**.5
    return ((x-2.1*B/n,y+2.1*A/n),(x+2.1*B/n,y-2.1*A/n))
