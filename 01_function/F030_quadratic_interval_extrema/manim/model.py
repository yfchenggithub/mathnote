"""Independent F030 interval model, using the source example (x-2)^2+1."""
import math
def f(x):return (x-2)**2+1
def extrema(m,n):
 if not m<n:raise ValueError('m < n required')
 near=min(n,max(m,2))
 left,right=f(m),f(n)
 far=[m,n] if math.isclose(left,right,rel_tol=0,abs_tol=1e-10) else [m if left>right else n]
 return {'nearest':near,'minimum':f(near),'farthest':far,'maximum':max(left,right)}
def general_extrema(a,h,k,m,n):
 if a==0 or not m<n:raise ValueError('a != 0 and m < n')
 near=min(n,max(m,h));far=m if abs(m-h)>=abs(n-h) else n
 vals=[a*(near-h)**2+k,a*(far-h)**2+k]
 return min(vals),max(vals)
