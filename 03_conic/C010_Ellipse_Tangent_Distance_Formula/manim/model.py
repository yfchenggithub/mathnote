"""C010 independent support-line, perpendicular-distance and pedal-circle model."""
from dataclasses import dataclass
from math import atan2,cos,isfinite,sin,sqrt


@dataclass(frozen=True)
class TangentDistanceModel:
    a: float=5.
    b: float=4.

    def __post_init__(self):
        if not(all(isfinite(v) for v in (self.a,self.b)) and self.a>self.b>0):
            raise ValueError('Require finite a>b>0')

    @property
    def c(self):
        return sqrt(self.a*self.a-self.b*self.b)

    def state(self,angle):
        u,v=cos(angle),sin(angle)
        h=sqrt(self.a*self.a*u*u+self.b*self.b*v*v)
        F1,F2=(-self.c,0.),(self.c,0.)
        d1,d2=h+self.c*u,h-self.c*u
        return {'normal':(u,v),'h':h,'P':(self.a*self.a*u/h,self.b*self.b*v/h),
                'F1':F1,'F2':F2,'H1':(F1[0]+d1*u,d1*v),
                'H2':(F2[0]+d2*u,d2*v),'Q':(h*u,h*v),'d1':d1,'d2':d2}

    def inverse_foot(self,H):
        """Right-focus pedal-circle inverse: (p-c)x+qy=a²-cp."""
        p,q=H
        return p-self.c,q,self.a*self.a-self.c*p


START=atan2(5,3)


def clip_line(A,B,D,xmax=5.7,ymax=5.5):
    points=[]
    if A==0 and B==0:
        raise ValueError('Invalid line')
    if B!=0:
        for x in (-xmax,xmax):
            y=(D-A*x)/B
            if abs(y)<=ymax+1e-10:
                points.append((x,y))
    if A!=0:
        for y in (-ymax,ymax):
            x=(D-B*y)/A
            if abs(x)<=xmax+1e-10 and all(abs(x-u)+abs(y-v)>1e-9 for u,v in points):
                points.append((x,y))
    return points[:2]
