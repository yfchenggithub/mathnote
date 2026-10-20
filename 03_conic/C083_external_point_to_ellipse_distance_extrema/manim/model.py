from math import sin,cos,hypot,pi
a,b=3.,2.
M=(4.,2.8)
def point(t):return a*cos(t),b*sin(t)
def distance(t):
    P=point(t);return hypot(P[0]-M[0],P[1]-M[1])
def derivative(t):
    return (a*a-b*b)*sin(t)*cos(t)-a*M[0]*sin(t)+b*M[1]*cos(t)
def critical():
    roots=[];N=4096
    for i in range(N):
        l=2*pi*i/N;r=2*pi*(i+1)/N
        if derivative(l)*derivative(r)>0:continue
        for j in range(55):
            q=(l+r)/2
            if derivative(l)*derivative(q)<=0:r=q
            else:l=q
        root=(l+r)/2
        if all(abs(root-z)>1e-7 for z in roots):roots.append(root)
    return roots
roots=critical()
tmin=min(roots,key=distance);tmax=max(roots,key=distance)
