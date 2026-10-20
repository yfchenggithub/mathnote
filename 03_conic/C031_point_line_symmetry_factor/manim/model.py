from math import cos,sin,hypot
A,B,C=1.,-2.,0.
def point(t): return 2*cos(t),1.5*sin(t)
def reflected(t):
    x,y=point(t); f=(A*x+B*y+C)/(A*A+B*B)
    return x-2*A*f,y-2*B*f
def foot(t):
    p,q=point(t),reflected(t); return ((p[0]+q[0])/2,(p[1]+q[1])/2)
def distance(t):
    p,h=point(t),foot(t); return hypot(p[0]-h[0],p[1]-h[1])
