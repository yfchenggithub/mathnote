from math import hypot,sqrt
A=(1.0,-2.0);B=(3.0,3.0);X0=9/5;MINIMUM=sqrt(29)
def state(x):
 p=(float(x),0.0);ap=hypot(x-A[0],A[1]);pb=hypot(x-B[0],B[1])
 return {'x':float(x),'p':p,'ap':ap,'pb':pb,'sum':ap+pb,'minimum':MINIMUM,'excess':ap+pb-MINIMUM}
