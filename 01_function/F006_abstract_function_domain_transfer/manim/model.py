def inner(x):return 2*x-1
def admissible(x):return 1<=inner(x)<=3
def audit():
    for i in range(401):
        x=-1+i/100
        assert admissible(x)==(1<=x<=2)
        assert abs((inner(x)+1)/2-x)<1e-14
    for t in [1,1.25,1.5,2,2.5,3]:assert admissible((t+1)/2)
    return 407
