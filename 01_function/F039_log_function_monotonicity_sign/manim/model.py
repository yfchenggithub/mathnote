"""F039 independent log model and fixed horizontal-level intersections."""
import math

def log_value(base, x):
    if not math.isfinite(base) or base<=0 or base==1 or not math.isfinite(x) or x<=0:
        raise ValueError('a>0, a!=1, x>0 required')
    return math.log(x)/math.log(base)

def level_intersection(base, y):
    if base<=0 or base==1:raise ValueError('legal logarithm base required')
    return math.exp(y*math.log(base))

def paired_bases(large):
    if not 2<=large<=4:raise ValueError('reviewed animation interval is [2,4]')
    return large,1/large

def parameter_example(a,x):
    if a<=0 or a==1 or 2*x-1<=0 or x+2<=0:return None
    return log_value(a,2*x-1)>log_value(a,x+2)
