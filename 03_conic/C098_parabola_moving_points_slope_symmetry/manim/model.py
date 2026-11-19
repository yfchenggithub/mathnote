def point(t,p=2):return (t*t/(2*p),t)
def state(u,p=2):
    v=-2*p-u
    return point(p,p),point(u,p),point(v,p)
def slope(a,b):return (b[1]-a[1])/(b[0]-a[0])
def audit():
    count=0
    for p in [0.5,1,2,3]:
      for i in range(101):
        u=p*(-.4+1.1*i/100);a,m,n=state(u,p)
        assert abs(slope(a,m)+slope(a,n))<1e-10
        assert abs(slope(m,n)+1)<1e-10
        for x,y in [a,m,n]:assert abs(y*y-2*p*x)<1e-10
        count+=1
    return count
