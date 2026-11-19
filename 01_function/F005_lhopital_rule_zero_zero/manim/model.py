def f(x):return x*x-1
def g(x):return x-1
def ratio(x):
    if x==1:raise ValueError('0/0 is undefined')
    return f(x)/g(x)
def audit():
    for i in range(1,201):
        h=i/250
        for x in [1-h,1+h]:assert abs(ratio(x)-(x+1))<1e-12
        assert abs((f(1+h)-f(1))/h-(2+h))<1e-12
    assert g(1)==0 and f(1)==0
    return 401
