from math import cos,pi
def f(x):return cos(pi*x)
def pair(a,t):return ((a-t,f(a-t)),(a+t,f(a+t)))
def is_axis(a):return abs(a-round(a))<1e-7
