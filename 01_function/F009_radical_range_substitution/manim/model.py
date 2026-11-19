import math
def substitution(x):return math.sqrt(x-1)
def original(x):return (substitution(x)-2)**2
def transformed(t):return (t-2)**2
def audit():
    for i in range(401):
        x=2+3*i/400;t=substitution(x)
        assert 1<=t<=2 and abs(x-(t*t+1))<1e-12
        assert original(x)==transformed(t) and 0<=original(x)<=1
    assert original(2)==1 and original(5)==0
    return 403
