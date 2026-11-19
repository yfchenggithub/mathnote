import math
def exact(x):return math.exp(x)
def quadratic(x):return 1+x+x*x/2
def residual(x):
    if x==0:raise ValueError('The quotient is undefined at zero')
    return (math.expm1(x)-x)/(x*x)
def audit():
    for i in range(-250,251):
        x=i/500
        assert abs(exact(x)-quadratic(x))<=math.exp(.5)*abs(x)**3/6+1e-15
        if x:assert abs(residual(x)-.5)<.1
    assert abs(residual(.0001)-.5)<.00002
    assert abs(residual(-.0001)-.5)<.00002
    return 503
