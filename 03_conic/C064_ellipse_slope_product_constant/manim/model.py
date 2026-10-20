from math import cos,sin,cosh,sinh
KIND='ellipse'
a,b=(3.,2.) if KIND=='ellipse' else (1.5,1.)
def point(t):return (a*cos(t),b*sin(t)) if KIND=='ellipse' else (a*cosh(t),b*sinh(t))
def slopes(t):
    x,y=point(t)
    if abs(x-a)<1e-10 or abs(x+a)<1e-10:raise ValueError('Axis vertices excluded')
    return y/(x+a),y/(x-a)
def product(t):
    k,l=slopes(t);return k*l
