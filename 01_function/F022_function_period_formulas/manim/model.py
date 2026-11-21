import math
def phi(u):
 if u==1:raise ValueError("pole")
 return (u+1)/(u-1)
def f(x):return 2 if math.floor(x)%2==0 else 3
def state(x):return tuple((x+j,f(x+j)) for j in range(3))
