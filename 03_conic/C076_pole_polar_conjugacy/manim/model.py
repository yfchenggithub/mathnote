a,b=2.5,1.5
P=(3.5,.8)
def Q(t):return (1-P[1]*t/b**2)*a*a/P[0],t
def bilinear(U,V):return U[0]*V[0]/a**2+U[1]*V[1]/b**2
def line(U):
    A,B=U[0]/a**2,U[1]/b**2;n=(A*A+B*B)**.5
    foot=(A/(n*n),B/(n*n))
    return ((foot[0]-4*B/n,foot[1]+4*A/n),(foot[0]+4*B/n,foot[1]-4*A/n))
