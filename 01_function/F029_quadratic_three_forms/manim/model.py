"""F029 independent model: fixed roots, nonzero leading coefficient."""
def value(x,a):
 if a==0: raise ValueError('A quadratic requires a != 0')
 return a*(x-1)*(x-3)
def expanded(x,a): return a*x*x-4*a*x+3*a
def vertex(a):
 if a==0: raise ValueError('a != 0')
 return (2,-a)
