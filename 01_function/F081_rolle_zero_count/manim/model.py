"""Independent mathematical models for F081; no renderer dependency."""
import math

def equal_height(x, amplitude=1.0, skew=0.0, mixture=0.0):
    polynomial=1+amplitude*(1-x*x)*(1+skew*x)
    wave=1+.85*math.sin(2*math.pi*(x+1))
    return (1-mixture)*polynomial+mixture*wave

def equal_slope(x, amplitude=1.0, skew=0.0, mixture=0.0):
    return (1-mixture)*amplitude*(skew-2*x-3*skew*x*x)+mixture*.85*2*math.pi*math.cos(2*math.pi*(x+1))

def stationary(skew):
    # Stable rationalization of (-1+sqrt(1+3s²))/(3s), including s=0.
    return skew/(1+math.sqrt(1+3*skew*skew))

WAVE_STATIONARY=(-.75,-.25,.25,.75)

def cubic(x,t=0.0):return x*x*x-3*x+t
def cubic_slope(x):return 3*x*x-3

def cubic_roots(t):
    """Distinct real roots, isolated on monotonic branches; exact boundary cases."""
    if abs(t-2)<1e-10:return [-2.0,1.0]
    if abs(t+2)<1e-10:return [-1.0,2.0]
    if abs(t)<1e-12:return [-math.sqrt(3),0.0,math.sqrt(3)]
    bound=3+abs(t)
    cuts=(-bound,-1.0,1.0,bound)
    result=[]
    for lo,hi in zip(cuts,cuts[1:]):
        if cubic(lo,t)*cubic(hi,t)>=0:continue
        for _ in range(55):
            mid=(lo+hi)/2
            if cubic(lo,t)*cubic(mid,t)<=0:hi=mid
            else:lo=mid
        result.append((lo+hi)/2)
    return result

def visible_cubic(t,limit=5.3):
    """Actual sampled curve segments inside the explicitly fixed viewport."""
    segments=[];current=[]
    for i in range(601):
        x=-2.35+4.7*i/600;y=cubic(x,t)
        if abs(y)<=limit:current.append((x,y))
        elif current:
            if len(current)>1:segments.append(current)
            current=[]
    if len(current)>1:segments.append(current)
    return segments
