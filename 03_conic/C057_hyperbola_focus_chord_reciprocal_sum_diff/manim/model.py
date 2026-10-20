from math import sin,cos,sqrt,hypot
a,b=1.5,1.; c=sqrt(a*a+b*b)
def endpoints(t):
    u,v=cos(t),sin(t); A=u*u/a**2-v*v/b**2; B=2*c*u/a**2; C=c*c/a**2-1
    if abs(A)<1e-10: raise ValueError('Asymptote-parallel direction loses one finite endpoint')
    roots=[(-B+sign*sqrt(B*B-4*A*C))/(2*A) for sign in (-1,1)]
    return tuple((c+r*u,r*v) for r in roots)
def reciprocal(t):
    A,B=endpoints(t); r=hypot(A[0]-c,A[1]); s=hypot(B[0]-c,B[1])
    return 1/r+1/s if A[0]*B[0]>0 else abs(1/r-1/s)
