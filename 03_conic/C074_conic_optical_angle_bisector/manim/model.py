from math import sin,cos,cosh,sinh,sqrt,hypot,acos
def unit(v):
    n=hypot(*v);return v[0]/n,v[1]/n
def state(kind,t):
    a,b,p=2.7,1.8,1.
    if kind=='ellipse':
        c=sqrt(a*a-b*b);P=(a*cos(t),b*sin(t));F=(-c,0);G=(c,0);normal=unit((P[0]/a**2,P[1]/b**2))
    elif kind=='hyperbola':
        a,b=1.5,1.;c=sqrt(a*a+b*b);P=(a*cosh(t),b*sinh(t));F=(-c,0);G=(c,0);normal=unit((P[0]/a**2,-P[1]/b**2))
    else:
        P=(t*t/(2*p),t);F=(p/2,0);G=(P[0]+2.3,P[1]);normal=unit((-p,t))
    u=unit((F[0]-P[0],F[1]-P[1]));v=unit((G[0]-P[0],G[1]-P[1]))
    bis=unit((u[0]+v[0],u[1]+v[1]))
    return P,F,G,u,v,bis,normal
def angles(kind,t):
    P,F,G,u,v,w,n=state(kind,t)
    return tuple(acos(max(-1,min(1,q[0]*w[0]+q[1]*w[1])))*180/3.141592653589793 for q in (u,v))
