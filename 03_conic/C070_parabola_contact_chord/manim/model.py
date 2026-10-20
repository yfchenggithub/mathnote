from math import sin,cos,atan2,acos,sqrt,hypot
KIND='parabola'
a,b,p=2.5,1.5,1.
if KIND in ('hyperbola','monge'):a,b=1.5,1.
def state(t):
    if KIND in ('ellipse','monge'):
        if KIND=='ellipse':P=(1.4*a*cos(t),1.4*b*sin(t))
        else:
            r=sqrt(a*a+b*b);P=(r*cos(t),r*sin(t))
        x,y=P[0]/a,P[1]/b
        z=atan2(y,x);d=acos(1/hypot(x,y))
        return P,(a*cos(z+d),b*sin(z+d)),(a*cos(z-d),b*sin(z-d))
    if KIND=='hyperbola':
        P=(0,t);y=-b*b/t;x=a*sqrt(1+y*y/(b*b))
        return P,(x,y),(-x,y)
    P=(-1.,t);d=sqrt(t*t+2*p)
    return P,((t+d)**2/(2*p),t+d),((t-d)**2/(2*p),t-d)
def curve(t,s=1):
    if KIND in ('ellipse','monge'):return a*cos(t),b*sin(t)
    if KIND=='hyperbola':
        from math import sinh,cosh
        return s*a*cosh(t),b*sinh(t)
    return t*t/(2*p),t
def polar(P,Q):
    x,y=P;X,Y=Q
    if KIND in ('ellipse','monge'):return x*X/a**2+y*Y/b**2-1
    if KIND=='hyperbola':return x*X/a**2-y*Y/b**2-1
    return y*Y-p*(X+x)
def angle(t):
    P,A,B=state(t);u=(A[0]-P[0],A[1]-P[1]);v=(B[0]-P[0],B[1]-P[1])
    return acos(max(-1,min(1,(u[0]*v[0]+u[1]*v[1])/(hypot(*u)*hypot(*v)))))*180/3.141592653589793
