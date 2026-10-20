p=1.
def state(t,d):
    A=(t-d,(t-d)**2/(2*p));B=(t+d,(t+d)**2/(2*p))
    P=(t,(t*t-d*d)/(2*p));M=((A[0]+B[0])/2,(A[1]+B[1])/2)
    return A,B,P,M
def area(t,d):
    A,B,P,M=state(t,d)
    return abs((A[0]-P[0])*(B[1]-P[1])-(B[0]-P[0])*(A[1]-P[1]))/2
