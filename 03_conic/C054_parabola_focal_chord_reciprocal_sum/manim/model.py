from math import sin,cos,hypot
p=1.5
def endpoints(t):
    u,v=cos(t),sin(t)
    if abs(v)<1e-9: raise ValueError('No finite focal chord parallel to axis')
    plus=p/(1-u); minus=p/(1+u)
    return ((p/2+plus*u,plus*v),(p/2-minus*u,-minus*v))
def state(t):
    A,B=endpoints(t); r=hypot(A[0]-p/2,A[1]); s=hypot(B[0]-p/2,B[1])
    return dict(r=r,s=s,length=hypot(A[0]-B[0],A[1]-B[1]),reciprocal=1/r+1/s,xproduct=A[0]*B[0],yproduct=A[1]*B[1])
