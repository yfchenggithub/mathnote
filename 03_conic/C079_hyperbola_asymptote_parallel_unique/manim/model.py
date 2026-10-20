a,b=2.,1.2
k=b/a
def point(m):
    if abs(m)<1e-10:raise ValueError('The asymptote has no finite intersection')
    x=-a*(b*b+m*m)/(2*b*m)
    return x,k*x+m
