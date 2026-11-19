import math
def exact(x):return math.exp(x)
def rational(x):return (x*x+6*x+12)/(x*x-6*x+12)
def error(x):return exact(x)-rational(x)
def audit():
    for i in range(501):
        x=i/500
        assert x*x-6*x+12>0
        assert -1e-15<=error(x)<=3*x**5/665+1e-15
    assert abs(rational(0)-1)<1e-15
    return 502
