def continuous(x):return 2*x+1
def jump(x):
    if not 0<=x<=1:raise ValueError('Outside domain')
    return x if x<1 else 2
def audit():
    for i in range(401):
        x=3*i/400;y=continuous(x);assert 1<=y<=7 and abs((y-1)/2-x)<1e-12
        u=i/400;z=jump(u);assert 0<=z<1 or z==2
    assert jump(0)==0 and jump(1)==2
    return 403
