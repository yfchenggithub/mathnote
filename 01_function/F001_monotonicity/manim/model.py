def f(x):return x**3-3*x+1
def df(x):return 3*x*x-3
def audit():
    for i in range(401):
        x=-2+4*i/400
        assert (df(x)>0)==(abs(x)>1)
        h=1e-5
        assert abs((f(x+h)-f(x-h))/(2*h)-df(x))<1e-7
    assert f(-1)==3 and f(1)==-1
    return 403
