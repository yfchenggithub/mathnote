from math import sin,pi
A=1.0
def f(x):return 2**sin(pi*x)
def state(x):return tuple((x+k*A,f(x+k*A)) for k in range(3))
