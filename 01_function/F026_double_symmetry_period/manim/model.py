from math import cos,pi
def f(x):return cos(pi*x/2)
def state(x):return ((x,f(x)),(-x,f(-x)),(4+x,f(4+x)))
