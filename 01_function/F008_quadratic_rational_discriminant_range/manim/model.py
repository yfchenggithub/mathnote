import math
def f(x):return 2+1/(x*x+1)
def discriminant(t):return 4*(3-t)*(t-2)
def roots(t):
    if not 2<t<=3:return []
    q=math.sqrt(max(0,(3-t)/(t-2)))
    return [0.] if q==0 else [-q,q]
def audit():
    for i in range(1,501):
        t=2+i/500
        for x in roots(t):assert abs(f(x)-t)<1e-12
        assert discriminant(t)>=0
    assert discriminant(2)==0 and roots(2)==[]
    assert roots(3)==[0.] and roots(3.1)==[]
    return 503
