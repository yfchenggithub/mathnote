from math import sin,cos,hypot
def endpoints(t):return (-1.8,-1.8*t+.4),(1.8,1.8*t+.4)
def length(t):
    A,B=endpoints(t);return hypot(A[0]-B[0],A[1]-B[1])
