from math import sin,pi
A=2.0
def f(x):return sin(pi*x/2)
def state(x):return tuple((x+k*A,f(x+k*A)) for k in range(3))
