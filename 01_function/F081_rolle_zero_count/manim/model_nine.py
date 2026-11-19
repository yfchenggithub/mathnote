"""F081: exact piecewise cubic models, independent of animation and other UIDs."""
from itertools import product

# Match the formal explanation's rise/flat/fall row and column order.
COEFFICIENTS=(1,0,-1)
CASES=tuple(product(COEFFICIENTS,repeat=2))

def f(x,a,b):return (a if x<=0 else b)*x**3
def df(x,a,b):return 0.0 if x==0 else 3*(a if x<0 else b)*x*x
def quotient(h,a,b):
    if h==0:raise ValueError('A difference quotient requires h != 0')
    return (a if h<0 else b)*h*h
def trend(k):return {1:'升',0:'平',-1:'降'}[k]
def note(a,b):
    if (a,b)==(1,-1):return '先升后降：在原点掉头'
    if (a,b)==(-1,1):return '先降后升：在原点掉头'
    if (a,b)==(1,1):return '一直上升，原点处也能有水平切线'
    if (a,b)==(-1,-1):return '一直下降，原点处也能有水平切线'
    if (a,b)==(0,0):return '整段恒为 0：没有升降，也没有掉头'
    return '进出水平段：原点处切线仍然水平'

def tangent_endpoints(x,a,b,half=.13):
    y=f(x,a,b);k=df(x,a,b)
    return ((x-half,y-half*k),(x+half,y+half*k))
