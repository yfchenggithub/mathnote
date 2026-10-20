from math import sin,cos,sqrt,hypot
a,b=3.,2.
c=sqrt(a*a-b*b); e=c/a
def point(t): return a*cos(t),b*sin(t)
def radius(t,i):
    x,y=point(t); return hypot(x-(-c if i==1 else c),y)
