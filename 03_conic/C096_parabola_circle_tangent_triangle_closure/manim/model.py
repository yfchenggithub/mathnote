"""C096: independently computed tangent-chord closure, from the formal source."""
import math

def point(t,k=1.0):
    return (t*t/k,t)

def state(a,k=1.0,r=1.0):
    if k<=0 or r<=0 or abs(a*a-r*r)<1e-12:
        raise ValueError('Need k,r>0 and two distinct finite other endpoints')
    h=r+r*r/k
    A=a*a-r*r;B=2*k*r*a;C=r*r*(2*k*r+r*r-a*a)
    delta=B*B-4*A*C
    if delta<=0:raise ValueError('Need two distinct roots')
    roots=sorted([(-B+math.sqrt(delta))/(2*A),(-B-math.sqrt(delta))/(2*A)],reverse=True)
    b,c=roots
    return {'parameters':(a,b,c),'points':tuple(point(t,k) for t in (a,b,c)),'center':(h,0.),'radius':r,'k':k}

def line(u,v,k=1.):
    return (k,-u-v,u*v)

def foot(center,coefficients):
    x,y=center;A,B,C=coefficients;q=(A*x+B*y+C)/(A*A+B*B)
    return (x-q*A,y-q*B)

def distance(center,coefficients):
    x,y=center;A,B,C=coefficients
    return abs(A*x+B*y+C)/math.hypot(A,B)

def clip_line(coefficients,xmin=-.5,xmax=4.7,ymin=-2.5,ymax=2.5):
    A,B,C=coefficients;hits=[]
    for y in (ymin,ymax):
        x=-(B*y+C)/A
        if xmin-1e-9<=x<=xmax+1e-9:hits.append((x,y))
    if abs(B)>1e-12:
        for x in (xmin,xmax):
            y=-(A*x+C)/B
            if ymin-1e-9<=y<=ymax+1e-9:hits.append((x,y))
    unique=[]
    for p in hits:
        if not any(math.dist(p,q)<1e-8 for q in unique):unique.append(p)
    if len(unique)<2:raise ValueError('Line misses view')
    return unique[0],unique[-1]

def audit():
    count=0
    for k in [.5,1.,2.,4.]:
      for r in [.5,1.,1.5]:
       for j in range(-22,23):
        s=state(r*j/100,k,r);a,b,c=s['parameters'];points=s['points'];M=s['center']
        assert min(abs(a-b),abs(a-c),abs(b-c))>1e-4
        for x,y in points:assert abs(y*y-k*x)<1e-10
        for u,v in [(a,b),(a,c),(b,c)]:
            L=line(u,v,k);T=foot(M,L)
            assert abs(distance(M,L)-r)<1e-10
            assert abs(L[0]*T[0]+L[1]*T[1]+L[2])<1e-10
            assert abs(math.dist(M,T)-r)<1e-10
            assert abs((T[0]-M[0])*(-L[1])+(T[1]-M[1])*L[0])<1e-10
        count+=1
    s=state(0);a,b,c=s['parameters'];L=line(b,c)
    assert abs(L[1])<1e-12 and abs(-L[2]/L[0]-3)<1e-12
    for j in range(241):
        s=state(-.22+.44*j/240);a,b,c=s['parameters']
        for u,v in [(a,b),(a,c),(b,c)]:
            L=line(u,v);ends=clip_line(L)
            for x,y in ends:assert abs(L[0]*x+L[1]*y+L[2])<1e-10
    return count+242
