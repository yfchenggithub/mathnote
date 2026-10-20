from math import sin,cos,hypot
lam=2.; a=1.
center=(lam*lam+1)/(lam*lam-1)*a
radius=2*a*lam/abs(lam*lam-1)
def point(t): return center+radius*cos(t),radius*sin(t)
def ratio(t):
    x,y=point(t); return hypot(x+a,y)/hypot(x-a,y)
