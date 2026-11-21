def f(x):
 z=x%4
 return z if z<=1 else (2-z if z<=3 else z-4)
def segment(n):return ((n,f(n)),(n+1,f(n+1)))
