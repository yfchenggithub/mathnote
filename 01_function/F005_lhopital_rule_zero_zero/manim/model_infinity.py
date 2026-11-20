"""F005 formal example 5: infinity/infinity, x tending to +infinity."""
def numerator(x): return 2*x*x+3*x+1
def denominator(x): return x*x+1
def numerator_prime(x): return 4*x+3
def denominator_prime(x): return 2*x
def ratio(x): return numerator(x)/denominator(x)
def derivative_ratio(x):
    if x == 0: raise ValueError('g_prime is zero')
    return numerator_prime(x)/denominator_prime(x)
def ratio_error(x): return (3*x-1)/(x*x+1)
def derivative_error(x): return 1.5/x
