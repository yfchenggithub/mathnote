from math import sin,cos,sqrt,hypot
a,b=3.,2.; c=sqrt(a*a-b*b); e=c/a
def endpoints(t):
    r=b*b/(a+c*cos(t)); s=b*b/(a-c*cos(t))
    return ((c+r*cos(t),r*sin(t)),(c-s*cos(t),-s*sin(t)))
def ratio(t):
    A,B=endpoints(t); return hypot(A[0]-c,A[1])/hypot(B[0]-c,B[1])
