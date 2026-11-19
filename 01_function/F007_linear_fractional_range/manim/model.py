def f(x):return 2+3/(x-1)
def inverse(t):
    if t==2:raise ValueError('Excluded output')
    return 1+3/(t-2)
def audit():
    for i in range(-400,401):
        t=i/50
        if t==2:continue
        x=inverse(t);assert x!=1 and abs(f(x)-t)<1e-11
    return 800
